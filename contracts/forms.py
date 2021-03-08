from django import forms
from django.core.exceptions import ValidationError
from containers.models import Container


class QueuedContainerForm(forms.Form):
    def __init__(self, contract, from_container, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.contract = contract
        self.from_container = from_container
        self.container_weights = {}
        self.json = []
        if contract.pend_containers:
            entry = {}
            for c in contract.pend_containers:
                if c["container"] == from_container:
                    for container, weight in c["distribution"].items():
                        entry.update({container: weight})
            # self.container_weights.update({
            #     c["container"]: c["weight"] for c in contract.pend_containers
            # })
            self.container_weights.update(entry)
        else:
            self.container_weights.update({
                c["container"]: c["weight"] for c in contract.curr_containers
            })
        print(repr(self.container_weights))
        self.from_container_weight = int(self.container_weights[from_container])
        for c in Container.objects.filter(company_code=contract.company_code):
            self.fields[c.unit_descriptor] = forms.IntegerField(
                required=False, initial=self.container_weights.get(c.unit_descriptor)
            )

    @property
    def get_json(self):
        return self.json

    def clean(self):
        print("Starting to clean")
        cleaned_data = super().clean()

        company_containers = {
            c.unit_descriptor
            for c in Container.objects.filter(company_code=self.contract.company_code)
        }
        pending_weight_total = sum(
            cleaned_data.get(c, 0) or 0 for c in company_containers
        )
        print(cleaned_data)
        print(repr(pending_weight_total))
        print(repr(self.from_container_weight))
        if pending_weight_total > self.contract.total_weight:
            print("BAD WEIGHTs")
            raise ValidationError(
                "Container weights must total to the contract's total weight."
            )

        return cleaned_data
