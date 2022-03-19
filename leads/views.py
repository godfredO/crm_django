from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views  import generic
from .models import Lead , Agent, Category
from .forms import (
    LeadForm, 
    LeadModelForm, 
    CustomUserCreationForm, 
    AssignAgentForm, 
    LeadCategoryUpdateForm, 
    CategoryModelForm
    )
from django.urls import reverse
from agents.mixins import OrganiserAndLoginRequiredMixin

class SignUpView(generic.CreateView):
    template_name = "registration/signup.html"
    form_class = CustomUserCreationForm
    
    def get_success_url(self):
        return reverse('login')

class LandingPageView(generic.TemplateView):
    template_name = "landing.html"


class LeadListView(LoginRequiredMixin, generic.ListView):
    template_name = 'leads/lead_list.html'
    context_object_name = 'leads'

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organiser:
            queryset = Lead.objects.filter(
                organisation=user.userprofile, 
                agent__isnull=False
            )
        else:
            # filter for agent's organisation
            queryset = Lead.objects.filter(
                organisation=user.agent.organisation, 
                agent__isnull=False
            )
            # filter for the agent that is logged in
            queryset = queryset.filter(agent__user=user)
        return queryset

    
    def get_context_data(self, **kwargs):
        user = self.request.user
        context= super(LeadListView, self).get_context_data(**kwargs)
        if user.is_organiser:
            queryset = Lead.objects.filter(
                organisation=user.userprofile, 
                agent__isnull=True
            )
            context.update({
                "unassigned_leads": queryset
            })
        return context




class LeadDetailView(LoginRequiredMixin,generic.DetailView):
    template_name = 'leads/lead_detail.html'
    context_object_name = 'lead'

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organiser:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            # filter for agent's organisation
            queryset = Lead.objects.filter(organisation=user.agent.organisation)
            # filter for the agent that is logged in
            queryset = queryset.filter(agent__user=user)
        return queryset


class LeadCreateView(OrganiserAndLoginRequiredMixin,generic.CreateView):
    template_name = "leads/lead_create.html"
    form_class = LeadModelForm

    def get_success_url(self):
        return reverse('leads:list')
    
    def form_valid(self,form):
        lead = form.save(commit=False)
        lead.organisation = self.request.user.userprofile
        lead.save()
        # To send an email
        send_mail(
            subject="A lead has been created",
            message="Go to the site to see the new lead",
            from_email = "test@test.com",
            recipient_list = ["test2@test.com"]  
        )
        messages.success(self.request, "You have successfully created a lead")
        return super(LeadCreateView, self).form_valid(form)



class LeadUpdateView(OrganiserAndLoginRequiredMixin,generic.UpdateView):
    template_name = "leads/lead_update.html"
    form_class = LeadModelForm

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        queryset = Lead.objects.filter(organisation=user.userprofile)
        return queryset

    def get_success_url(self):
        return reverse('leads:list')


class LeadDeleteView(OrganiserAndLoginRequiredMixin,generic.DeleteView):
    template_name = 'leads/lead_delete.html'
    

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        queryset = Lead.objects.filter(organisation=user.userprofile)
        return queryset

    def get_success_url(self):
        return reverse('leads:list')



class AssignAgentView(OrganiserAndLoginRequiredMixin, generic.FormView):
    template_name = "leads/assign_agent.html"
    form_class = AssignAgentForm


    def get_form_kwargs(self, **kwargs):
        kwargs = super(AssignAgentView, self).get_form_kwargs(**kwargs)
        kwargs.update({
            'request':self.request
        })
        return kwargs

    def get_success_url(self):
        return reverse("leads:list")

    def form_valid(self,form):
        agent = form.cleaned_data["agent"]
        lead = Lead.objects.get(id=self.kwargs["pk"])
        lead.agent = agent
        lead.save()
        return super(AssignAgentView, self).form_valid(form)




class CategoryListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/category_list.html"
    context_object_name = "category_list"

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        user = self.request.user
        if user.is_organiser:
            queryset = Lead.objects.filter(
                organisation=user.userprofile
            )
        else:
            # filter for agent's organisation
            queryset = Lead.objects.filter(
                organisation=user.agent.organisation,
            )
        context.update({
            "unassigned_lead_count": queryset.filter(category__isnull=True).count()
        })
        return context

    def get_queryset(self):
        user = self.request.user
        # initial queryset of categories for the entire organisation
        if user.is_organiser:
            queryset = Category.objects.filter(
                organisation=user.userprofile
            )
        else:
            # filter for agent's organisation
            queryset = Category.objects.filter(
                organisation=user.agent.organisation,
            )
        return queryset
    


class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "leads/category_detail.html"
    context_object_name = "category"

    # def get_context_data(self, **kwargs):
    #     context = super(CategoryDetailView, self).get_context_data(**kwargs)
    #     leads = self.get_object().leads.all() #leads is related name bcos of related key
    #     context.update({
    #         "leads": leads
    #     })
    #     return context

    def get_queryset(self):
        user = self.request.user
        # initial queryset of categories for the entire organisation
        if user.is_organiser:
            queryset = Category.objects.filter(
                organisation=user.userprofile
            )
        else:
            # filter for agent's organisation
            queryset = Category.objects.filter(
                organisation=user.agent.organisation,
            )
        return queryset
    


class CategoryCreateView(OrganiserAndLoginRequiredMixin,generic.CreateView):
    template_name = "leads/category_create.html"
    form_class = CategoryModelForm

    def get_success_url(self):
        return reverse('leads:category-list')
    
    def form_valid(self,form):
        category = form.save(commit=False)
        category.organisation = self.request.user.userprofile
        category.save()
        return super(CategoryCreateView, self).form_valid(form)
    


class CategoryUpdateView(OrganiserAndLoginRequiredMixin,generic.UpdateView):
    template_name = "leads/category_update.html"
    form_class = CategoryModelForm

    def get_success_url(self):
        return reverse('leads:category-list')
    
    def get_queryset(self):
        user = self.request.user
        # initial queryset of categories for the entire organisation
        if user.is_organiser:
            queryset = Category.objects.filter(
                organisation=user.userprofile
            )
        else:
            # filter for agent's organisation
            queryset = Category.objects.filter(
                organisation=user.agent.organisation,
            )
        return queryset
    

class CategoryDeleteView(OrganiserAndLoginRequiredMixin,generic.DeleteView):
    template_name = 'leads/category_delete.html'
    

    def get_queryset(self):
        user = self.request.user
        # initial queryset of categories for the entire organisation
        if user.is_organiser:
            queryset = Category.objects.filter(
                organisation=user.userprofile
            )
        else:
            # filter for agent's organisation
            queryset = Category.objects.filter(
                organisation=user.agent.organisation,
            )
        return queryset

    def get_success_url(self):
        return reverse('leads:category-list')




class LeadCategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_category_update.html"
    form_class = LeadCategoryUpdateForm


    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organiser:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            # filter for agent's organisation
            queryset = Lead.objects.filter(organisation=user.agent.organisation)
            # filter for the agent that is logged in
            queryset = queryset.filter(agent__user=user)
        return queryset


    def get_success_url(self):
        return reverse('leads:detail', kwargs={'pk': self.get_object().id})


class LeadJsonView(generic.View):

    def get(self, request, *args, **kwargs):

        qs = Lead.objects.all()

        return JsonResponse({
            "name": "Test",
            "age": 25
        })

# def lead_list(request):
#     leads = Lead.objects.all()
#     context = {
#         "leads": leads
#     } 
#     return render(request, 'leads/lead_list.html', context)



# def lead_detail(request, pk):
#     lead = Lead.objects.get(id=pk)
#     context = {
#         'lead': lead
#     }
#     return render(request, 'leads/lead_detail.html', context)


# def lead_create(request):
#     form = LeadModelForm()
#     if request.method == "POST":
#        form = LeadModelForm(request.POST)
#        if form.is_valid():
#            form.save()
#            return redirect(reverse('leads:list'))
#     context = {
#         'form': form
#     }
#     return render(request, "leads/lead_create.html", context)


# def lead_update(request,pk):
#     lead = Lead.objects.get(id=pk) 
#     form = LeadModelForm(instance=lead)
#     if request.method == "POST":
#        form = LeadModelForm(request.POST, instance=lead)
#        if form.is_valid():
#            form.save()
#            return redirect(reverse('leads:list'))
#     context= {
#         'form': form,
#         'lead': lead
#     }
#     return render(request, "leads/lead_update.html", context)


# def lead_delete(request,pk):
#     lead = Lead.objects.get(id=pk) 
#     lead.delete()
#     return redirect(reverse('leads:list'))






# def lead_update(request,pk):
#     lead = Lead.objects.get(id=pk)
#     form = LeadForm()
#     if request.method == "POST":
#        form = LeadForm(request.POST)
#        if form.is_valid():
#            first_name = form.cleaned_data['first_name']
#            last_name = form.cleaned_data['last_name']
#            age = form.cleaned_data['age']
#            lead.first_name = first_name
#            lead.last_name = last_name
#            lead.age = age
#            lead.save()
#            return redirect(reverse('leads:list')) 
#     context= {
#         'form': form,
#         'lead': lead
#     }
#     return render(request, "leads/lead_update.html", context)


# # def lead_create(request):
#     form = LeadForm()
#     if request.method == "POST":
#        form = LeadForm(request.POST)
#        if form.is_valid():
#            first_name = form.cleaned_data['first_name']
#            last_name = form.cleaned_data['last_name']
#            age = form.cleaned_data['age']
#            agent = Agent.objects.first()
#            Lead.objects.create(
#                first_name=first_name, 
#                last_name=last_name, 
#                age=age, 
#                agent=agent
#                )
#            return redirect(reverse('leads:list'))
#     context = {
#         'form': form
#     }
#     return render(request, "leads/lead_create.html", context)

