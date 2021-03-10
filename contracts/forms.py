from django import forms
from django.core.exceptions import ValidationError
from containers.models import Container
import json


class QueuedContainerForm(forms.Form):
    def __init__(self, contract, from_container, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.contract = contract
        self.from_container = from_container
        self.container_weights = {}
        self.json = []
        if contract.pend_containers:
            self.json = json.loads(str(self.contract.pend_containers).replace("'", '"'))
            # entry = {}
            # for c in contract.pend_containers:
            #     if c["container"] == from_container:
            #         for container in c["distribution"]:
            #             entry.update({container["container"]: container["weight"]})
            # self.container_weights.update({
            #     c["container"]: c["weight"] for c in contract.pend_containers
            # })
                # self.container_weights.update(entry)
            entry = {}
            for c in contract.pend_containers:
                # print("c: ", repr(c))
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
                else:
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
            # self.container_weights.update({
            #     c["container"]: c["weight"] for c in contract.curr_containers
            # })
            entry = {}
            for c in contract.curr_containers:
                # print("c: ", repr(c))
                j_content = {}
                if c["container"] == from_container:
                    j_list = []
                    for container in c["distribution"]:
                        entry.update({container["container"]: str(container["weight"])})
                        j_list.append({"container": container["container"], "weight": str(container["weight"])})
                    j_content = {"container": from_container, "distribution": j_list}
                    self.json.append(j_content)
                self.container_weights.update(entry)
        # print(repr(self.container_weights))
        # print("JSON: ", repr(self.json))
        self.from_container_weight = int(self.container_weights[from_container])
        print("from_weight: ", self.from_container_weight)
        for c in Container.objects.filter(company_code=contract.company_code):
            self.fields[c.unit_descriptor] = forms.IntegerField(
                required=False, initial=self.container_weights.get(c.unit_descriptor, 0)
            )

    @property
    def contract_weight(self):
        total = 0
        containers_with_weight = []
        for transfer in self.contract.pend_containers:
            for distrib in transfer["distribution"]:
                weight = distrib["weight"]
                total += weight
                if weight > 0:
                    containers_with_weight.append(distrib["container"])
        if total != self.contract.total_weight:
            for transfer in self.contract.pend_containers:
                for distrib in transfer["distribution"]:
                    weight = distrib["weight"]
                    if distrib["container"] not in containers_with_weight:
                        total += weight
                        if weight > 0:
                            containers_with_weight.append(distrib["container"])
        print(total)
        return total


    def clean(self):
        # print("Starting to clean")
        cleaned_data = super().clean()

        company_containers = {
            c.unit_descriptor
            for c in Container.objects.filter(company_code=self.contract.company_code)
        }
        pending_weight_total = sum(
            cleaned_data.get(c, 0) or 0 for c in company_containers
        )
        # print(cleaned_data)
        # print(repr(pending_weight_total))
        # print(repr(self.from_container_weight))
        print("total_weight: ", self.contract.total_weight)
        if self.contract.pend_containers:
            weight = self.contract_weight
        else:
            weight = self.contract.total_weight
        if pending_weight_total > weight:
            print("BAD WEIGHTs")
            raise ValidationError(
                "Container weights must total to the contract's total weight."
            )

        return cleaned_data

    @property
    def get_json(self):
        for transfer in self.json:
            if transfer["container"] == self.from_container:
                distrib = [
                    {"container": c, "weight": w}
                    for c, w in self.cleaned_data.items()
                    if w is not None
                ]
                # del transfer["distribution"]
                transfer["distribution"] = distrib
        return json.loads(str(self.json).replace("'", '"'))