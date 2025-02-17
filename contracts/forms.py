from django import forms
from django.core.exceptions import ValidationError
from containers.models import Container
from django.shortcuts import get_object_or_404, redirect, render
from contracts.models import Contract
import json

# --- JSON FORMAT GUIDE ---
# Each entry will be a dictionary in the root list.
# Entries have a 'container' key and 'distribution' key:
# 'container' == from_container
# 'distribution' == list of dictionaries
# The 'distribution' list will have dictionaries for each company container:
# 'container' == container.unit_descriptor
# 'weight' == weight stored in contract for that container
# Example:
# [
#   {'container': 'ABC-123', 'distribution':
#       [
#           {'container': 'ABC-123', 'weight': 200}, 
#           {'container': 'ABC-456', 'weight': 300}, 
#       ]
#   },
#   {'container': 'ABC-789', 'distribution':
#       [
#           {'container': 'ABC-789', 'weight': 100}, 
#           {'container': 'ABC-321', 'weight': 700}, 
#       ]
#   },
# ]

class QueuedContainerForm(forms.Form):
    def __init__(self, contract, from_container, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.contract = contract
        self.from_container = from_container # The container selected to transfer from
        self.container_weights = {}
        self.json = []


        print("QUEUED FORM")
        if contract.pend_containers:
            # For some reason, calling the JSONField pend_containers as it is freezes the website, so I call it as a string, then convert it back to JSON
            self.json = json.loads(str(self.contract.pend_containers).replace("'", '"'))

            for c in self.json:
                print("JSON_C: ", c)
                if c["container"] == "reallocate":
                    self.json.remove(c)
            
            print("after Json: ", self.json)

            # Generate JSON format and container weights dictionary from pending containers
            entry = {}
            for c in contract.pend_containers:
                print("pend_c: ", c)
                j_content = {}
                # Only update the from_container entry in pend_containers
                if c["container"] == from_container:
                    j_list = []
                    for container in c["distribution"]:
                        entry.update({container["container"]: str(container["weight"])})
                        j_list.append({"container": container["container"], "weight": str(container["weight"])})
                    j_content = {"container": from_container, "distribution": j_list}
                    # Determine if from_container entry already exists. If so, then update. Else, add a new entry
                    exists = False
                    distribution = None
                    for dictionary in self.json:
                        if dictionary["container"] == self.from_container:
                            exists = True
                            distribution = dictionary['distribution']
                            break
                    if not exists:
                        self.json.append(j_content)
                    else:
                        c['distribution'] = distribution
                else:
                    # If from_container is not in pend_containers, then we must make a new entry
                    for c in contract.curr_containers:
                        j_content = {}
                        if c["container"] == from_container:
                            j_list = []
                            for container in c["distribution"]:
                                entry.update({container["container"]: str(container["weight"])})
                                j_list.append({"container": container["container"], "weight": str(container["weight"])})
                            j_content = {"container": from_container, "distribution": j_list}
                            exists = False
                            distribution = None
                            for dictionary in self.json:
                                if dictionary["container"] == self.from_container:
                                    exists = True
                                    distribution = dictionary['distribution']
                                    break
                            if not exists:
                                self.json.append(j_content)
                            else:
                                c['distribution'] = distribution
                self.container_weights.update(entry)
        else:
            # If pend_containers does not exist, then we must make a new entry
            entry = {}
            for c in contract.curr_containers:
                j_content = {}
                if c["container"] == from_container:
                    j_list = []
                    for container in c["distribution"]:
                        entry.update({container["container"]: str(container["weight"])})
                        j_list.append({"container": container["container"], "weight": str(container["weight"])})
                    j_content = {"container": from_container, "distribution": j_list}
                    self.json.append(j_content)
                self.container_weights.update(entry)
        # Generate Integer fields for each container that belongs to the contract's company
        for c in Container.objects.filter(company_code=contract.company_code):
            self.fields[c.unit_descriptor] = forms.FloatField(
                required=False, 
                initial=self.container_weights.get(c.unit_descriptor, 0), 
                widget=forms.TextInput(attrs={'class': 'form-control'})
            )

    @property
    def transfer_weight(self):
        # Sum all allocated weight so that users can exceed a container's original weight, but not the contract's total weight remaining
        total = 0
        # Sum all weights in curr_containers
        for transfer in self.contract.curr_containers:
            print(transfer)
            if transfer["container"] == self.from_container:
                for distrib in transfer["distribution"]:
                    weight = float(distrib["weight"])
                    print("weight: ", weight)
                    total += weight
        return total


    def clean(self):
        cleaned_data = super().clean()

        company_containers = {
            c.unit_descriptor
            for c in Container.objects.filter(company_code=self.contract.company_code)
        }
        pending_weight_total = sum(
            cleaned_data.get(c, 0) or 0 for c in company_containers
        )
        weight = self.contract.total_weight
        if pending_weight_total > weight:
            print("Pend: ", pending_weight_total)
            print("Weight: ", weight)
            print("Container weights must total to the contract's total weight.")
            self.errors["total"] = "Container weights must total to the contract's total weight."
            print(repr(self.errors))
            raise ValidationError(
                "Container weights must total to the contract's total weight."
            )

        return cleaned_data

    @property
    def get_json(self):
        # Returns full JSON string to be stored in pend_containers feild
        print("\n", self.cleaned_data.items())
        print("from: ", repr(self.from_container))
        for transfer in self.json:
            if transfer["container"] == self.from_container:
                distrib = []
                for c, w in self.cleaned_data.items():
                    print(repr(w))
                    if w == None or w == 0:
                        if c == self.from_container:
                            distrib.append({"container": c, "weight": 0})
                    else:
                        distrib.append({"container": c, "weight": w})

                print(distrib, "\n")
                transfer["distribution"] = distrib
        return json.loads(str(self.json).replace("'", '"'))


class ReallocateForm(forms.Form):
    def __init__(self, contract, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.contract = contract
        self.container_weights = {}
        self.json = []
        self.contract_weight = float(self.contract.total_weight)

        print("REALLOCATE FORM")
        if contract.pend_containers:
            # Generate JSON format and container weights dictionary from pending containers
            entry = {}
            for c in contract.pend_containers:
                j_content = {}
                # Only update the from_container entry in pend_containers
                if c["container"] == 'reallocate':
                    print("1")
                    j_list = []
                    for container in c["distribution"]:
                        entry.update({container["container"]: str(container["weight"])})
                        j_list.append({"container": container["container"], "weight": str(container["weight"])})
                    j_content = {"container": 'reallocate', "distribution": j_list}
                    # Determine if 'reallocate' entry already exists. If so, then update. Else, add a new entry
                    exists = False
                    distribution = None
                    for dictionary in self.json:
                        if dictionary["container"] == 'reallocate':
                            exists = True
                            distribution = dictionary['distribution']
                            break
                    if not exists:
                        self.json.append(j_content)
                    else:
                        c['distribution'] = distribution
                else:
                    # If 'reallocate' is not in pend_containers, then we must make a new entry
                    print("2")
                    for c in contract.pend_containers:
                        j_content = {}
                        j_list = []
                        for container in c["distribution"]:
                            entry.update({container["container"]: str(container["weight"])})
                            j_list.append({"container": container["container"], "weight": str(container["weight"])})
                        j_content = {"container": 'reallocate', "distribution": j_list}
                        exists = False
                        distribution = None
                        for dictionary in self.json:
                            if dictionary["container"] == 'reallocate':
                                exists = True
                                distribution = dictionary['distribution']
                                break
                        if not exists:
                            self.json.append(j_content)
                        else:
                            c['distribution'] = distribution
        else:
            # If pend_containers does not exist, then we must make a new entry
            print("3")
            entry = {}
            for c in contract.curr_containers:
                j_content = {}
                j_list = []
                for container in Container.objects.filter(company_code=contract.company_code):
                    if container.unit_descriptor == c["container"]:
                        for curr_container in c['distribution']:
                            if curr_container == container.unit_descriptor:
                                entry.update({curr_container["container"]: str(curr_container["weight"])})
                                j_list.append({"container": curr_container["container"], "weight": str(curr_container["weight"])})
                    else:
                        entry.update({container.unit_descriptor: 0})
                        j_list.append({"container": container.unit_descriptor, "weight": 0})
                    j_content = {"container": 'reallocate', "distribution": j_list}
            self.json.append(j_content)

        self.container_weights.update(entry)
        print("cont_weights: ", self.container_weights)
        # Generate Integer fields for each container that belongs to the contract's company
        for c in Container.objects.filter(company_code=contract.company_code):
            self.fields[c.unit_descriptor] = forms.FloatField(
                required=False, 
                initial=self.container_weights.get(c.unit_descriptor, 0), 
                widget=forms.TextInput(attrs={'class': 'form-control'})
            )

    def clean(self):
        cleaned_data = super().clean()

        company_containers = {
            c.unit_descriptor
            for c in Container.objects.filter(company_code=self.contract.company_code)
        }
        print("company_containers: ", company_containers)
        pending_weight_total = float(sum(
            cleaned_data.get(c, 0) or 0 for c in company_containers
        ))
        print("pending_weight_total: ", pending_weight_total)
        weight = self.contract_weight
        if pending_weight_total != weight:
            print("Pend: ", pending_weight_total)
            print("Weight: ", weight)
            print("Container weights must total to the contract's total weight.")
            self.errors["total"] = "All weight must be allocated."
            raise ValidationError(
                "Container weights must total to the contract's total weight."
            )

        return cleaned_data

    @property
    def get_json(self):
        print("b: ", self.json)
        # Returns full JSON string to be stored in pend_containers feild
        for transfer in self.json:
            if transfer["container"] == 'reallocate':
                distrib = []
                for c, w in self.cleaned_data.items():
                    print(repr(w))
                    if w == None or w == 0:
                        pass
                    else:
                        distrib.append({"container": c, "weight": w})

                print(distrib, "\n")
                transfer["distribution"] = distrib
        print("a: ", self.json)
        return json.loads(str(self.json).replace("'", '"'))

class ClearPendingForm(forms.Form):
    def __init__(self, contract, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.contract = contract
    def clear_pending(request, id):
        contract.pend_containers = None

