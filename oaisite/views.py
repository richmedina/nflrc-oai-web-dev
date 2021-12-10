import json

from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView

from braces.views import LoginRequiredMixin
from haystack.generic_views import SearchView

from oaiharvests.models import Community, Collection, Record, MetadataElement
from .models import OAISitePage, OAISitePost
from .forms import PageUpdateForm, PostUpdateForm


class HomeView(TemplateView):
    template_name = 'home.html'
    queryset = None

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        try:
            journal = Community.objects.all()[0]
            context['keywords'] =  journal.aggregate_keywords()
            context['volumes'] = journal.list_collections_by_volume()
            
            current_vol = Collection.objects.all().order_by('-name')[0]
            context['current_vol'] = current_vol.title_tuple()
            context['current_vol_toc'] = current_vol.list_toc_by_page()
    
            articles = context['current_vol_toc']['Article'].items()
            article_data = next(iter(articles))[1]
            # context['latest_article'] = article_data['records'][1]
            
            latest_special_issue = journal.get_special_issues()[0]
            context['special_issue'] = latest_special_issue.title_tuple()
            
            context['byline'] = OAISitePost.objects.get(pk=5)

            features = OAISitePost.objects.filter(featured=True).order_by('-featured_rank') 
            if features: context['featured_posts'] = features[:2]
        except Exception as e:
            messages.info(self.request, e)
        
        return context


class PreviousIssuesView(TemplateView):
    template_name = 'previous_issues.html'

    def get_context_data(self, **kwargs):
        context = super(PreviousIssuesView, self).get_context_data(**kwargs)
        journal = Community.objects.all()[0]
        context['volumes'] = journal.list_collections_by_volume()
        context['latest'] = [(vol, vol.list_records()) for vol in Collection.objects.all().order_by('-name')][0]
        context['curr_page'] = 'previous_issues'
        return context


class SpecialIssuesView(TemplateView):
    template_name = 'special_issues.html'

    def get_context_data(self, **kwargs):
        context = super(SpecialIssuesView, self).get_context_data(**kwargs)
        journal = Community.objects.all()[0]
        context['special_issues'] = []
        for j in journal.get_special_issues():
            context['special_issues'].append(j.title_tuple())

        context['curr_page'] = 'special_issues'
        return context


class CommunityView(DetailView):
    model = Community
    template_name = 'journal_view.html'

    def get_context_data(self, **kwargs):
        context = super(CommunityView, self).get_context_data(**kwargs)
        context['collections'] = self.get_object().list_collections()
        return context


class CollectionListView(ListView):
    model = Collection
    template_name = 'issue_list.html'

    def get_context_data(self, **kwargs):
        context = super(CollectionListView, self).get_context_data(**kwargs)
        return context


class CollectionView(DetailView):
    model = Collection
    template_name = 'issue_view.html'
    queryset = None

    def get_context_data(self, **kwargs):
        context = super(CollectionView, self).get_context_data(**kwargs)
        context['toc'] = self.get_object().list_toc_by_page()
        context['size'] = len(context['toc'])
        context['issue'] = self.get_object().title_tuple()
        return context


class ItemView(DetailView):
    model = Record
    template_name = 'record_view.html'

    def get_context_data(self, **kwargs):
        context = super(ItemView, self).get_context_data(**kwargs)
        context['item_data'] = self.get_object().as_display_dict()
        bitstream = context['item_data']['bitstream'][0]
        
        # PATCH to handle two different data structures in db (list or string)
        #   related to introduced modification to collect bitstreams as la ist 
        #   in utils/get_bitstream_url()

        context['bitstreams'] = []
        if not isinstance(bitstream, list):
            bitstream = [bitstream]    
        
        for bit_url in bitstream:
            if not bit_url.startswith('https:'): 
                bit_url = bit_url.replace('http://', 'https://', 1)
            bit_url_name = bit_url[bit_url.rfind('/')+1:]
            context['bitstreams'].append((bit_url, bit_url_name))
        
        # END PATCH
        
        return context


class ItemViewFull(DetailView):
    model = Record
    template_name = 'record_view_full.html'

    def get_context_data(self, **kwargs):
        context = super(ItemViewFull, self).get_context_data(**kwargs)
        context['item_data'] = self.get_object().as_dict()
        return context


class PageView(DetailView):
    model = OAISitePage
    template_name = 'page_view.html'
    context_object_name = 'page'

    def get(self, request, *args, **kwargs):
        if not self.get_object().published:
            # will redirect to login required view
            return redirect('staff_page_view', item=self.get_object().id)
        return super(PageView, self).get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(PageView, self).get_context_data(*args, **kwargs)
        # context['admin_edit'] = reverse('admin:lltsite_storypage_change', args=(self.get_object().id,))
        context['curr_page'] = self.get_object().id
        return context


class PageUpdateView(LoginRequiredMixin, UpdateView):
    model = OAISitePage
    template_name = 'page_view_update.html'
    form_class = PageUpdateForm


class PageViewPrivate(LoginRequiredMixin, DetailView):
    model = OAISitePage
    template_name = 'page_view.html'
    context_object_name = 'page'

    # def get_context_data(self, *args, **kwargs):
    #     context = super(PageViewPrivate, self).get_context_data(*args, **kwargs)
    #     return context


class PostListView(ListView):
    model = OAISitePost
    template_name = 'post_list_view.html'

    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        if not self.request.user.is_staff:
            self.object_list = self.object_list.filter(published=True)
        context['object_list'] = self.object_list.order_by('-modified')    
        return context


class PostView(DetailView):
    model = OAISitePost
    template_name = 'post_view.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        if not self.get_object().published:
            # will redirect to login required view
            return redirect('staff_post_view', pk=self.get_object().id)
        return super(PostView, self).get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(PostView, self).get_context_data(*args, **kwargs)
        # context['admin_edit'] = reverse('admin:lltsite_storypage_change', args=(self.get_object().id,))
        # context['curr_page'] = self.get_object().id
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = OAISitePost
    template_name = 'post_view_create.html'
    form_class = PostUpdateForm
    

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = OAISitePost
    template_name = 'post_view_update.html'
    form_class = PostUpdateForm


class PostViewPrivate(LoginRequiredMixin, DetailView):
    model = OAISitePost
    template_name = 'post_view.html'
    context_object_name = 'post'

    # def get_context_data(self, *args, **kwargs):
    #     context = super(PostViewPrivate, self).get_context_data(*args, **kwargs)
    #     return context


class SearchHaystackView(SearchView):
    def get_context_data(self, *args, **kwargs):
        context = super(SearchHaystackView, self).get_context_data(*args, **kwargs)

        keylist = ['Assessment/Testing','Behavior-tracking Technology','Blended/Hybrid Learning and Teaching','Code Switching','Collaborative Learning','Computer-Mediated Communication','Concordancing','Corpus','Culture','Data-driven Learning','Digital Literacies','Discourse Analysis','Distance/Open Learning and Teaching','Eye Tracking','Feedback','Game-based Learning and Teaching','Grammar','Human-Computer Interaction','Indigenous Languages','Instructional Context','Instructional Design','Language for Special Purposes','Language Learning Strategies','Language Maintenance','Language Teaching Methodology','Learner Attitudes','Learner Autonomy','Learner Identity','Less Commonly Taught Languages','Listening','Meta Analysis','Mobile Learning','MOOCs','Multiliteracies','Natural Language Processing','Open Educational Resources','Pragmatics','Pronunciation','Reading','Research Methods','Social Context','Sociocultural Theory','Social Networking','Speaking','Speech Recognition','Speech Synthesis','Task-based Learning and Teaching','Teacher Education','Telecollaboration','Ubiquitous Learning and Teaching','Virtual Environments','Vocabulary','Writing']

        cols_length = len(keylist) // 3
        keytable = []
        for i in range(0, len(keylist), cols_length):
            keytable.append(keylist[i:i+cols_length])

        authorlist = []
        for i in MetadataElement.objects.filter(element_type='contributor.author'):
            for j in json.loads(i.element_data):                
                # swap the first and last so last appears after first.
                n = j.split(',')
                try:
                    authorlist.append((n[1].strip(), n[0].strip()))
                except:
                    pass
        
        authorlist = set(authorlist)
        authorlist = sorted(authorlist, key=lambda author: author[1].lower())

        # will create n sets of authors to be rendered in columns
        # cols_length = len(authorlist) / 6
        # authortable = []
        # for i in range(0, len(authorlist), cols_length):
        #     authortable.append(authorlist[i:i+cols_length])

        context['authortable'] = authorlist # using flat list for now. authortable an option if needed.
        context['keytable'] = keytable
        return context

#DEL
# class KeywordBrowseView(TemplateView):
#     template_name = 'page_keyword_browse.html'

#     def get_context_data(self, **kwargs):
#         context = super(KeywordBrowseView, self).get_context_data(**kwargs)
        
#         keylist = ['Assessment/Testing','Behavior-tracking Technology','Blended/Hybrid Learning and Teaching','Code Switching','Collaborative Learning','Computer-Mediated Communication','Concordancing','Corpus','Culture','Data-driven Learning','Digital Literacies','Discourse Analysis','Distance/Open Learning and Teaching','Eye Tracking','Feedback','Game-based Learning and Teaching','Grammar','Human-Computer Interaction','Indigenous Languages','Instructional Context','Instructional Design','Language for Special Purposes','Language Learning Strategies','Language Maintenance','Language Teaching Methodology','Learner Attitudes','Learner Autonomy','Learner Identity','Less Commonly Taught Languages','Listening','Meta Analysis','Mobile Learning','MOOCs','Multiliteracies','Natural Language Processing','Open Educational Resources','Pragmatics','Pronunciation','Reading','Research Methods','Social Context','Sociocultural Theory','Social Networking','Speaking','Speech Recognition','Speech Synthesis','Task-based Learning and Teaching','Teacher Education','Telecollaboration','Ubiquitous Learning and Teaching','Virtual Environments','Vocabulary','Writing']

#         cols_length = len(keylist) / 3
#         keytable = []
#         for i in range(0, len(keylist), cols_length):
#             keytable.append(keylist[i:i+cols_length])

#         context['keytable'] = keytable
#         return context


# class UpdateImpactFactorView(LoginRequiredMixin, UpdateView):
#     model = ImpactFactor
#     template_name = 'impact_factor_update.html'
#     form_class = UpdateImpactFactorForm
#     success_url = reverse_lazy('home')   


