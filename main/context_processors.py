from main.models import Company


def company_context(request):
    """Add company to all templates."""
    company = Company.objects.first()
    return {'company': company}
