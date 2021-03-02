from django.forms import Form

class QueueForm(Form):
    def __init__(self, contract, *args, **kwargs):
        super().__init__(*args, **kwargs)
        containers = Container.objects.filter(
            company_code=contract.company_code
        ) 
        for container in containers:
            self.fields[container.code] = forms.IntegerField(required=False)