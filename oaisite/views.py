import json
from datetime import datetime

from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView

from braces.views import LoginRequiredMixin
from haystack.generic_views import SearchView
import requests

from oaiharvests.models import Community, Collection, Record, MetadataElement
from .models import OAISitePage, OAISitePost, OAISiteSupplementaryCollection
from .forms import PageUpdateForm, PostCreateForm, PostUpdateForm


def get_related_item(handle=''):
    """Returns a related object from the db based handle. Searches Record and Collection
    Handle is in the format: 'https://hdl.handle.net/nnnnn/nnnnnn'"""
    try:    
        handle = handle.split('/')[-2:]
        query = 'oai:scholarspace.manoa.hawaii.edu:' + '/'.join(handle)
        relobj = Record.objects.filter(identifier=query)
        if not relobj:
            query = 'col_' + '_'.join(handle)
            relobj = Collection.objects.filter(identifier=query)

        if relobj:
            return relobj[0].get_absolute_url()

    except Exception as e:
        print(e)
        pass
    return ''

class BaseSideMenuMixin(object):
    def get_context_data(self, **kwargs):
        context = super(BaseSideMenuMixin, self).get_context_data(**kwargs)
        context['byline'] = OAISitePage.objects.get(slug='byline')
        context['impact_factor'] = OAISitePage.objects.get(slug='impact-factor')

        return context


class HomeView(BaseSideMenuMixin, TemplateView):
    template_name = 'home.html'
    queryset = None

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        try:
            journal = Community.objects.all()[0]
            context['keywords'] =  journal.aggregate_keywords()
            try:
                context['volumes'] = journal.list_collections_by_volume()
            except Exception as e:
                print(e, 'Cannot load all collections')
            
            collection_list = Collection.objects.all().order_by('-name')
            for i in collection_list:
                if not i.special_issue:
                    context['current_vol'] = i.title_tuple()
                    context['current_vol_toc'] = i.list_toc_by_page()
                    break

            latest_special_issue = journal.get_special_issues()[0]
            context['special_issue'] = latest_special_issue.title_tuple()
            
            features = OAISitePost.objects.filter(featured=True).order_by('-featured_rank') 
            if features: 
                context['featured_posts'] = features[:2]

        except Exception as e:
            messages.info(self.request, e)

        try:    
            articles = context['current_vol_toc']['Article'].items()
            article_data = next(iter(articles))[1]
            context['latest_article'] = article_data['records'][0]
            context['article_count'] = len(article_data['records'])
        except:
            pass

        try:
            columns = context['current_vol']['object'].list_records_by_type('Column')
            context['column_count'] = len(columns)
            latest_column = columns[0]
            for i in columns:
                curr = datetime.strptime(i.get_metadata_item('date.accessioned')[0][0], '%Y-%m-%dT%H:%M:%SZ')
                latest = datetime.strptime(latest_column.get_metadata_item('date.accessioned')[0][0], '%Y-%m-%dT%H:%M:%SZ')
                if curr > latest:
                    latest_column = i
            context['latest_column'] = latest_column

        except:
            pass

        try:
            reviews = context['current_vol_toc']['Review'].items()
            reviews_data = next(iter(reviews))[1]
            context['review_count'] = len(reviews_data['records'])
        except:
            pass

        try:
            # article_reviews = context['current_vol_toc']['Article_Review'].items()
            # article_reviews_data = next(iter(article_reviews))[1]
            # context['article_review_count'] = len(article_reviews_data['records'])
            context['article_review_count'] = 0
        except:
            pass        
        return context


class PreviousIssuesView(BaseSideMenuMixin, TemplateView):
    template_name = 'previous_issues.html'

    def get_context_data(self, **kwargs):
        context = super(PreviousIssuesView, self).get_context_data(**kwargs)
        journal = Community.objects.all()[0]
        context['volumes'] = journal.list_collections_by_volume()
        context['latest'] = [(vol, vol.list_records()) for vol in Collection.objects.all().order_by('-name')][0]
        context['curr_page'] = 'previous_issues'
        return context


class SpecialIssuesView(BaseSideMenuMixin, TemplateView):
    template_name = 'special_issues.html'

    def get_context_data(self, **kwargs):
        context = super(SpecialIssuesView, self).get_context_data(**kwargs)
        specials = Collection.objects.filter(special_issue=True).order_by('-name')
        context['special_issues'] = [i.title_tuple() for i in specials]
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
        try:
            context['toc'] = self.get_object().list_toc_by_page()
            context['size'] = len(context['toc'])
            context['issue'] = self.get_object().title_tuple()
        except:
            context['issue'] = self.get_object().title_tuple()
        
        return context


class ItemView(DetailView):
    model = Record
    template_name = 'record_view.html'

    def get_context_data(self, **kwargs):
        context = super(ItemView, self).get_context_data(**kwargs)
        context['item_data'] = self.get_object().as_display_dict()
        try:
            bitstream = context['item_data']['bitstream'][0]

            context['bitstreams'] = []
            
            for bit_url in bitstream:
                if not bit_url[0].startswith('https:'): 
                    bit_url[0] = bit_url[0].replace('http://', 'https://', 1)
                context['bitstreams'].append((bit_url[0], bit_url[1]))
        except:
            pass
        
        return context


class ItemSlugView(DetailView):
    model = Record
    template_name = 'record_view.html'

    def get_context_data(self, **kwargs):
        context = super(ItemSlugView, self).get_context_data(**kwargs)
        context['item_data'] = self.get_object().as_display_dict()
        try:
            bitstream = context['item_data']['bitstream'][0]
            
            context['bitstreams'] = []
            
            for bit_url in bitstream:
                if not bit_url[0].startswith('https:'): 
                    bit_url[0] = bit_url[0].replace('http://', 'https://', 1)
                context['bitstreams'].append((bit_url[0], bit_url[1]))
        except:
            pass
            
        return context


class ItemViewFull(DetailView):
    model = Record
    template_name = 'record_view_full.html'

    def get_context_data(self, **kwargs):
        context = super(ItemViewFull, self).get_context_data(**kwargs)
        context['item_data'] = self.get_object().as_dict()
        return context


class MediaCollectionView(BaseSideMenuMixin, DetailView):
    model = OAISiteSupplementaryCollection
    template_name = 'media_collection_view.html'

    def get_context_data(self, **kwargs):
        context = super(MediaCollectionView, self).get_context_data(**kwargs)
        items = self.get_object().collection_id.list_records()

        context['items'] = []
        for i in items:
            r = i.as_dict()

            cleaned = {}
            try:
                cleaned['date_issued'] = [datetime.strptime(r['date.issued'][0], '%Y-%m-%d')]
                cleaned['title'] = r['title']
                cleaned['description'] = r['description']
                cleaned['bitstream'] = r['bitstream'][0][0]
                cleaned['external_url'] = r['relation.uri']
                cleaned['citation'] = r['identifier.citation']
                cleaned['length'] = r['format.extent']            
                cleaned['full_text'] = i.full_text
                cleaned['related'] = r['relation.isbasedon']
                if cleaned['related']:
                    cleaned['related'] = get_related_item(handle=cleaned['related'][0])

            except Exception as e:
                pass          
            context['items'].append(cleaned)
        
        context['curr_page'] = 'media'
        return context


class PageUpdateView(LoginRequiredMixin, UpdateView):
    model = OAISitePage
    template_name = 'page_view_update.html'
    form_class = PageUpdateForm
    

class PageView(BaseSideMenuMixin, DetailView):
    model = OAISitePage
    template_name = 'page_view.html'
    context_object_name = 'page'

    def get(self, request, *args, **kwargs):
        if not self.get_object().published:
            # will redirect to login required view
            return redirect('staff_page_view', pk=self.get_object().id)
        return super(PageView, self).get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(PageView, self).get_context_data(*args, **kwargs)
        # context['admin_edit'] = reverse('admin:lltsite_storypage_change', args=(self.get_object().id,))
        context['curr_page'] = self.get_object().id
        return context


class PageViewPrivate(LoginRequiredMixin, BaseSideMenuMixin, DetailView):
    model = OAISitePage
    template_name = 'page_view.html'
    context_object_name = 'page'

    # def get_context_data(self, *args, **kwargs):
    #     context = super(PageViewPrivate, self).get_context_data(*args, **kwargs)
    #     return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = OAISitePost
    template_name = 'post_view_create.html'
    form_class = PostCreateForm


class PostListView(BaseSideMenuMixin, ListView):
    model = OAISitePost
    template_name = 'post_list_view.html'

    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        context['feature_list'] = self.object_list.filter(featured=True).order_by('-featured_rank', '-modified')
        context['object_list'] = self.object_list.filter(featured=False).order_by('-modified')    
        if not self.request.user.is_staff:
            context['feature_list'] = context['feature_list'].filter(published=True)
            context['object_list'] = context['object_list'].filter(published=True)
        return context
    

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = OAISitePost
    template_name = 'post_view_update.html'
    form_class = PostUpdateForm


class PostViewPrivate(LoginRequiredMixin, DetailView):
    model = OAISitePost
    template_name = 'post_view.html'
    context_object_name = 'post'


class PostView(BaseSideMenuMixin, DetailView):
    model = OAISitePost
    template_name = 'post_view.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        if not self.get_object().published:
            return redirect('staff_post_view', pk=self.get_object().id)
        return super(PostView, self).get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(PostView, self).get_context_data(*args, **kwargs)
        return context


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



