from django import forms

class UploadForm(forms.Form):
    file = forms.FileField(label="Файл")
    fmt = forms.ChoiceField(
        label="Формат",
        choices=[("csv", "CSV"), ("xlsx", "XLSX")],
    )

class ExportForm(forms.Form):
    fmt = forms.ChoiceField(
        label="Формат выгрузки",
        choices=[("csv", "CSV"), ("xlsx", "XLSX")],
    )
    period = forms.ChoiceField(
        label="Фильтр по периоду",
        choices=[
            ("all", "Все контакты"),
            ("24h", "Созданные за последние 24 часа"),
        ],
        initial="all",
    )
