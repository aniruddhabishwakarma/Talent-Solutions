from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from main.models import Skill
from main.decorators import admin_required


@admin_required
def skill_list(request):
    """List all skills."""
    skills = Skill.objects.all()
    return render(request, 'my-admin/skills/list.html', {'skills': skills})


@admin_required
def skill_add(request):
    """Add a new skill."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()

        if not name:
            messages.error(request, 'Skill name is required.')
            return render(request, 'my-admin/skills/add.html')

        if Skill.objects.filter(name__iexact=name).exists():
            messages.error(request, 'Skill already exists.')
            return render(request, 'my-admin/skills/add.html', {'form_data': {'name': name}})

        try:
            skill = Skill(name=name)
            skill.save()
            messages.success(request, f'Skill "{name}" created successfully!')
            return redirect('skill_list')
        except Exception as e:
            messages.error(request, f'Error creating skill: {str(e)}')
            return render(request, 'my-admin/skills/add.html', {'form_data': {'name': name}})

    return render(request, 'my-admin/skills/add.html')


@admin_required
def skill_edit(request, slug):
    """Edit a skill."""
    skill = get_object_or_404(Skill, slug=slug)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()

        if not name:
            messages.error(request, 'Skill name is required.')
            return render(request, 'my-admin/skills/edit.html', {'skill': skill})

        if Skill.objects.filter(name__iexact=name).exclude(pk=skill.pk).exists():
            messages.error(request, 'Skill with this name already exists.')
            return render(request, 'my-admin/skills/edit.html', {'skill': skill})

        try:
            skill.name = name
            skill.save()
            messages.success(request, f'Skill "{name}" updated successfully!')
            return redirect('skill_list')
        except Exception as e:
            messages.error(request, f'Error updating skill: {str(e)}')
            return render(request, 'my-admin/skills/edit.html', {'skill': skill})

    return render(request, 'my-admin/skills/edit.html', {'skill': skill})


@admin_required
def skill_delete(request, slug):
    """Delete a skill."""
    skill = get_object_or_404(Skill, slug=slug)

    if request.method == 'POST':
        name = skill.name
        skill.delete()
        messages.success(request, f'Skill "{name}" deleted successfully!')
        return redirect('skill_list')

    return render(request, 'my-admin/skills/delete.html', {'skill': skill})
