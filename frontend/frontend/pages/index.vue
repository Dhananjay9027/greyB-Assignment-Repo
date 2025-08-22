<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <h1 class="text-2xl font-bold text-gray-900">
            🔬 Technical Document Search
          </h1>
          <div class="text-sm text-gray-500">
            Patents & Research Papers
          </div>
        </div>
      </div>
    </header>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Search Section -->
      <div class="bg-white rounded-lg shadow-sm p-6 mb-8">
        <div class="space-y-6">
          <!-- Query Input -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Search Query
            </label>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Enter your technical question or topic..."
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              @keyup.enter="performSearch"
            />
          </div>

          <!-- Filters Row -->
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <!-- Document Type -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Document Type
              </label>
              <select
                v-model="filters.docType"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="both">Both</option>
                <option value="patent">Patent Only</option>
                <option value="paper">Paper Only</option>
              </select>
            </div>

            <!-- Year Range -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Year From
              </label>
              <input
                v-model="filters.yearStart"
                type="number"
                placeholder="2010"
                min="1990"
                max="2024"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Year To
              </label>
              <input
                v-model="filters.yearEnd"
                type="number"
                placeholder="2024"
                min="1990"
                max="2024"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <!-- Min Citations -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Min Citations
              </label>
              <input
                v-model="filters.minCitations"
                type="number"
                placeholder="0"
                min="0"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <!-- Search Button -->
          <div class="flex justify-center">
            <button
              @click="performSearch"
              :disabled="!searchQuery.trim() || loading"
              class="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
            >
              {{ loading ? 'Searching...' : 'Search Documents' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Results Tabs -->
      <div v-if="searchResults.length > 0" class="bg-white rounded-lg shadow-sm">
        <div class="border-b border-gray-200">
          <nav class="flex space-x-8 px-6">
            <button
              @click="activeTab = 'results'"
              :class="[
                'py-4 px-1 border-b-2 font-medium text-sm',
                activeTab === 'results'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              ]"
            >
              Search Results ({{ searchResults.length }})
            </button>
            <button
              @click="activeTab = 'trends'"
              :class="[
                'py-4 px-1 border-b-2 font-medium text-sm',
                activeTab === 'trends'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              ]"
            >
              Trend Analysis
            </button>
            <button
              @click="activeTab = 'subtopics'"
              :class="[
                'py-4 px-1 border-b-2 font-medium text-sm',
                activeTab === 'subtopics'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              ]"
            >
              Sub-topics
            </button>
          </nav>
        </div>

        <div class="p-6">
          <!-- Results Tab -->
          <div v-if="activeTab === 'results'" class="space-y-4">
            <div v-for="result in searchResults" :key="result.document_id" 
                 class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div class="flex items-start justify-between mb-3">
                <div class="flex items-center space-x-3">
                  <span :class="[
                    'px-2 py-1 rounded-full text-xs font-medium',
                    result.doc_type === 'patent' 
                      ? 'bg-blue-100 text-blue-800' 
                      : 'bg-green-100 text-green-800'
                  ]">
                    {{ result.doc_type === 'patent' ? '📋 Patent' : '📄 Paper' }}
                  </span>
                  <span class="text-sm text-gray-500">
                    {{ result.publication_year }}
                  </span>
                  <span v-if="result.citation_count > 0" class="text-sm text-gray-500">
                    📊 {{ result.citation_count }} citations
                  </span>
                </div>
                <div class="text-sm text-blue-600 font-medium">
                  Score: {{ result.relevance_score.toFixed(3) }}
                </div>
              </div>
              
              <h3 class="font-semibold text-gray-900 mb-2">
                {{ result.title }}
              </h3>
              
              <p class="text-gray-600 text-sm leading-relaxed">
                {{ result.abstract.substring(0, 300) }}
                <span v-if="result.abstract.length > 300">...</span>
              </p>
              
              <div class="mt-3 text-xs text-gray-500">
                ID: {{ result.document_id }}
              </div>
            </div>
          </div>

          <!-- Trends Tab -->
          <div v-if="activeTab === 'trends'">
            <TrendAnalysis v-if="trendData" :data="trendData" />
            <div v-else class="text-center py-8">
              <button
                @click="analyzeTrends"
                :disabled="loadingTrends"
                class="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400"
              >
                {{ loadingTrends ? 'Analyzing...' : 'Analyze Trends' }}
              </button>
            </div>
          </div>

          <!-- Subtopics Tab -->
          <div v-if="activeTab === 'subtopics'">
            <SubtopicAnalysis v-if="subtopicData" :data="subtopicData" />
            <div v-else class="text-center py-8">
              <button
                @click="analyzeSubtopics"
                :disabled="loadingSubtopics"
                class="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400"
              >
                {{ loadingSubtopics ? 'Analyzing...' : 'Analyze Sub-topics' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="!loading && searchResults.length === 0 && searchQuery" 
           class="text-center py-12">
        <div class="text-gray-400 text-xl mb-4">🔍</div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">No results found</h3>
        <p class="text-gray-500">Try adjusting your search query or filters</p>
      </div>

      <!-- Getting Started -->
      <div v-if="!searchQuery && searchResults.length === 0" 
           class="bg-blue-50 rounded-lg p-8 text-center">
        <div class="text-blue-600 text-4xl mb-4">🚀</div>
        <h2 class="text-xl font-semibold text-gray-900 mb-2">
          Search Technical Documents
        </h2>
        <p class="text-gray-600 mb-4">
          Enter your technical question to search through patents and research papers
        </p>
        <div class="text-sm text-gray-500">
          <p>Examples:</p>
          <ul class="mt-2 space-y-1">
            <li>"machine learning algorithms for image recognition"</li>
            <li>"renewable energy storage solutions"</li>
            <li>"artificial intelligence in healthcare"</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

// State
const searchQuery = ref('')
const loading = ref(false)
const loadingTrends = ref(false)
const loadingSubtopics = ref(false)
const searchResults = ref([])
const trendData = ref(null)
const subtopicData = ref(null)
const activeTab = ref('results')

// Filters
const filters = reactive({
  docType: 'both',
  yearStart: '',
  yearEnd: '',
  minCitations: ''
})

// Config
const config = useRuntimeConfig()

// Methods
const performSearch = async () => {
  if (!searchQuery.value.trim()) return
  
  loading.value = true
  trendData.value = null
  subtopicData.value = null
  
  try {
    const searchParams = {
      query: searchQuery.value,
      top_k: 50,
      doc_type: filters.docType,
      year_start: filters.yearStart || null,
      year_end: filters.yearEnd || null,
      min_citations: filters.minCitations || null
    }
    
    const response = await $fetch(`${config.public.apiBase}/search`, {
  method: 'POST',
  body: searchParams
})

searchResults.value = response.results
    activeTab.value = 'results'
  } catch (error) {
    console.error('Search failed:', error)
    alert('Search failed. Please check if the backend is running.')
  } finally {
    loading.value = false
  }
}

const analyzeTrends = async () => {
  loadingTrends.value = true
  
  try {
    const searchParams = {
      query: searchQuery.value,
      top_k: 50,
      doc_type: filters.docType,
      year_start: filters.yearStart || null,
      year_end: filters.yearEnd || null,
      min_citations: filters.minCitations || null
    }
    
    const data = await $fetch(`${config.public.apiBase}/trend-analysis`, {
      method: 'POST',
      body: searchParams
    })
    
    trendData.value = data
  } catch (error) {
    console.error('Trend analysis failed:', error)
    alert('Trend analysis failed. Please try again.')
  } finally {
    loadingTrends.value = false
  }
}

const analyzeSubtopics = async () => {
  loadingSubtopics.value = true
  
  try {
    const requestData = {
      search_results: searchResults.value,
      n_clusters: Math.min(5, Math.floor(searchResults.value.length / 3))
    }
    
    const data = await $fetch(`${config.public.apiBase}/analyze-subtopics`, {
      method: 'POST',
      body: requestData
    })
    
    subtopicData.value = data
  } catch (error) {
    console.error('Subtopic analysis failed:', error)
    alert('Subtopic analysis failed. Please try again.')
  } finally {
    loadingSubtopics.value = false
  }
}

// SEO
useHead({
  title: 'Technical Document Search',
  meta: [
    { name: 'description', content: 'Search patents and research papers with AI-powered semantic search' }
  ]
})
</script>