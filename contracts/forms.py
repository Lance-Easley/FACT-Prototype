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
                    self.json.append(j_content)
                else:
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
        for c in Container.objects.filter(company_code=contract.company_code):
            self.fields[c.unit_descriptor] = forms.IntegerField(
                required=False, initial=self.container_weights.get(c.unit_descriptor)
            )


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
        if pending_weight_total > self.contract.total_weight:
            print("BAD WEIGHTs")
            raise ValidationError(
                "Container weights must total to the contract's total weight."
            )

        return cleaned_data

    @property
    def get_json(self):
        for transfer in self.json:
            if transfer["container"] == self.from_container:
                print("transfer::: ", transfer)
                distrib = [
                    {"container": c, "weight": w}
                    for c, w in self.cleaned_data.items()
                    if w is not None
                ]
                print("distrib::: ", distrib)
                print("T before: ", transfer)
                transfer["distribution"] = distrib
                print("T after: ", transfer)
        print("JSON::: ", repr(self.json))
        return json.loads(str(self.json).replace("'", '"'))