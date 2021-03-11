from django import forms
from django.core.exceptions import ValidationError
from containers.models import Container
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

        if contract.pend_containers:
            # For some reason, calling the JSONField pend_containers as it is freezes the website, so I call it as a string, then convert it back to JSON
            self.json = json.loads(str(self.contract.pend_containers).replace("'", '"'))
            # Generate JSON format and container weights dictionary from pending containers
            entry = {}
            for c in contract.pend_containers:
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

        self.from_container_weight = int(self.container_weights[from_container])
        # Generate Integer fields for each container that belongs to the contract's company
        for c in Container.objects.filter(company_code=contract.company_code):
            self.fields[c.unit_descriptor] = forms.IntegerField(
                required=False, initial=self.container_weights.get(c.unit_descriptor, 0)
            )

    @property
    def contract_weight(self):
        # Sum all allocated weight so that users can exceed a container's original weight, but not the contract's total weight remaining
        total = 0
        containers_with_weight = []
        # Sum all weights in pend_containers first
        for transfer in self.contract.pend_containers:
            for distrib in transfer["distribution"]:
                weight = distrib["weight"]
                total += weight
                if weight > 0:
                    containers_with_weight.append(distrib["container"])
        # if the pending container's weights do not take up full weight, grab from the unedited curr_containers
        if total != self.contract.total_weight:
            for transfer in self.contract.pend_containers:
                for distrib in transfer["distribution"]:
                    weight = distrib["weight"]
                    if distrib["container"] not in containers_with_weight:
                        total += weight
                        if weight > 0:
                            containers_with_weight.append(distrib["container"])
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
        if self.contract.pend_containers:
            weight = self.contract_weight
        else:
            weight = self.contract.total_weight
        if pending_weight_total > weight:
            raise ValidationError(
                "Container weights must total to the contract's total weight."
            )

        return cleaned_data

    @property
    def get_json(self):
        # Returns full JSON string to be stored in pend_containers feild
        for transfer in self.json:
            if transfer["container"] == self.from_container:
                distrib = [
                    {"container": c, "weight": w}
                    for c, w in self.cleaned_data.items()
                    if w is not None
                ]
                transfer["distribution"] = distrib
        return json.loads(str(self.json).replace("'", '"'))