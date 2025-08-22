<template>
  <div class="space-y-6">
    <!-- Overview -->
    <div class="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6">
      <h3 class="text-lg font-semibold mb-2">🔍 Sub-topic Analysis</h3>
      <p class="text-gray-600">
        Documents have been automatically clustered into {{ Object.keys(data.clusters || {}).length }} related sub-topics
        based on semantic similarity of their abstracts.
      </p>
    </div>

    <!-- Debug Info (remove in production) -->
    <div v-if="!data.clusters" class="bg-red-50 border border-red-200 rounded p-4">
      <p class="text-red-800">Debug: No clusters data found</p>
      <pre class="text-xs mt-2">{{ JSON.stringify(data, null, 2) }}</pre>
    </div>

    <!-- Clusters Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div v-for="(cluster, clusterId) in data.clusters" :key="clusterId"
           class="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
        
        <!-- Cluster Header -->
        <div class="flex items-start justify-between mb-4">
          <div class="flex-1">
            <h4 class="font-semibold text-gray-900 mb-2">
              {{ cluster.name || `Cluster ${parseInt(clusterId) + 1}` }}
            </h4>
            <div class="flex flex-wrap gap-1 mb-3">
              <span v-for="keyword in (cluster.keywords || [])" :key="keyword"
                    class="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                {{ keyword }}
              </span>
            </div>
          </div>
          
          <!-- Cluster Size Badge -->
          <div class="text-center">
            <div class="text-2xl font-bold text-gray-900">{{ getClusterSize(cluster) }}</div>
            <div class="text-xs text-gray-500">documents</div>
          </div>
        </div>

        <!-- Stats Grid -->
        <div class="grid grid-cols-2 gap-4 mb-4">
          <div class="bg-blue-50 rounded-lg p-3 text-center">
            <div class="text-lg font-bold text-blue-900">{{ getPatentCount(cluster) }}</div>
            <div class="text-blue-600 text-xs">Patents</div>
          </div>
          <div class="bg-green-50 rounded-lg p-3 text-center">
            <div class="text-lg font-bold text-green-900">{{ getPaperCount(cluster) }}</div>
            <div class="text-green-600 text-xs">Papers</div>
          </div>
        </div>

        <!-- Additional Stats -->
        <div class="grid grid-cols-2 gap-4 mb-4 text-sm">
          <div>
            <div class="text-gray-600">Time Span</div>
            <div class="font-medium">{{ getYearRange(cluster) }}</div>
          </div>
          <div>
            <div class="text-gray-600">Avg Citations</div>
            <div class="font-medium">{{ getAvgCitations(cluster) }}</div>
          </div>
        </div>

        <!-- Document Type Ratio Visualization -->
        <div class="mb-4">
          <div class="flex items-center justify-between text-sm text-gray-600 mb-2">
            <span>Document Mix</span>
            <span>{{ getDocumentRatio(cluster) }}</span>
          </div>
          <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div class="h-full flex">
              <div 
                class="bg-blue-500"
                :style="{ width: getPatentPercentage(cluster) + '%' }">
              </div>
              <div 
                class="bg-green-500"
                :style="{ width: getPaperPercentage(cluster) + '%' }">
              </div>
            </div>
          </div>
        </div>

        <!-- Sample Documents Preview -->
        <div class="border-t pt-4">
          <div class="flex items-center justify-between mb-3">
            <h5 class="text-sm font-medium text-gray-700">Sample Documents</h5>
            <button 
              @click="toggleClusterExpansion(clusterId)"
              class="text-blue-600 hover:text-blue-800 text-sm">
              {{ expandedClusters[clusterId] ? 'Show Less' : 'Show More' }}
            </button>
          </div>
          
          <div class="space-y-2">
            <div v-for="(doc, index) in getClusterDocuments(cluster, clusterId)" 
                 :key="doc.document_id || index"
                 class="p-2 bg-gray-50 rounded text-sm">
              <div class="flex items-start justify-between mb-1">
                <span :class="[
                  'px-2 py-0.5 rounded text-xs',
                  doc.doc_type === 'patent' 
                    ? 'bg-blue-100 text-blue-700' 
                    : 'bg-green-100 text-green-700'
                ]">
                  {{ doc.doc_type || 'unknown' }}
                </span>
                <span class="text-gray-500 text-xs">{{ doc.publication_year || 'N/A' }}</span>
              </div>
              <div class="font-medium text-gray-900 mb-1 line-clamp-1">
                {{ doc.title || 'Untitled' }}
              </div>
              <div class="text-gray-600 text-xs line-clamp-2">
                {{ (doc.abstract || '').substring(0, 150) }}...
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Cluster Comparison -->
    <div class="bg-white rounded-lg border p-6">
      <h3 class="text-lg font-semibold mb-4">📊 Cluster Comparison</h3>
      
      <!-- Size Comparison -->
      <div class="mb-6">
        <h4 class="font-medium text-gray-700 mb-3">Cluster Sizes</h4>
        <div class="space-y-2">
          <div v-for="(cluster, clusterId) in sortedClusters" :key="clusterId"
               class="flex items-center">
            <div class="w-32 text-sm text-gray-600">
              Cluster {{ parseInt(clusterId) + 1 }}
            </div>
            <div class="flex-1 mx-3">
              <div class="bg-gray-200 rounded-full h-3">
                <div 
                  class="h-3 bg-gradient-to-r from-blue-400 to-blue-600 rounded-full transition-all duration-500"
                  :style="{ width: (getClusterSize(cluster) / maxClusterSize * 100) + '%' }">
                </div>
              </div>
            </div>
            <div class="w-16 text-right text-sm font-medium">
              {{ getClusterSize(cluster) }}
            </div>
          </div>
        </div>
      </div>

      <!-- Citation Analysis -->
      <div>
        <h4 class="font-medium text-gray-700 mb-3">Average Citations by Cluster</h4>
        <div class="space-y-2">
          <div v-for="(cluster, clusterId) in citationSortedClusters" :key="clusterId"
               class="flex items-center">
            <div class="w-32 text-sm text-gray-600">
              Cluster {{ parseInt(clusterId) + 1 }}
            </div>
            <div class="flex-1 mx-3">
              <div class="bg-gray-200 rounded-full h-3">
                <div 
                  class="h-3 bg-gradient-to-r from-purple-400 to-purple-600 rounded-full transition-all duration-500"
                  :style="{ width: (getAvgCitations(cluster) / maxAvgCitations * 100) + '%' }">
                </div>
              </div>
            </div>
            <div class="w-16 text-right text-sm font-medium">
              {{ getAvgCitations(cluster) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Keywords Cloud -->
    <div class="bg-white rounded-lg border p-6">
      <h3 class="text-lg font-semibold mb-4">🏷️ Key Terms Across All Clusters</h3>
      <div class="flex flex-wrap gap-2">
        <span v-for="(keyword, index) in getAllKeywords()" :key="keyword.word"
              :class="[
                'px-3 py-1 rounded-full font-medium transition-colors cursor-default',
                getKeywordColor(index)
              ]"
              :style="{ fontSize: getKeywordSize(keyword.count) + 'px' }">
          {{ keyword.word }}
          <span class="text-xs opacity-75">({{ keyword.count }})</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  data: {
    type: Object,
    required: true
  }
})

// State
const expandedClusters = ref({})

// Helper methods for safe data access
const getClusterSize = (cluster) => {
  return cluster?.stats?.size || cluster?.documents?.length || 0
}

const getPatentCount = (cluster) => {
  if (cluster?.stats?.patents !== undefined) return cluster.stats.patents
  return cluster?.documents?.filter(doc => doc.doc_type === 'patent').length || 0
}

const getPaperCount = (cluster) => {
  if (cluster?.stats?.papers !== undefined) return cluster.stats.papers
  return cluster?.documents?.filter(doc => doc.doc_type === 'paper').length || 0
}

const getYearRange = (cluster) => {
  if (cluster?.stats?.year_range) return cluster.stats.year_range
  
  const docs = cluster?.documents || []
  if (docs.length === 0) return 'N/A'
  
  const years = docs.map(doc => doc.publication_year).filter(Boolean)
  if (years.length === 0) return 'N/A'
  
  return `${Math.min(...years)} - ${Math.max(...years)}`
}

const getAvgCitations = (cluster) => {
  if (cluster?.stats?.avg_citations !== undefined) return cluster.stats.avg_citations
  
  const docs = cluster?.documents || []
  const citations = docs.filter(doc => doc.citation_count > 0).map(doc => doc.citation_count)
  
  if (citations.length === 0) return 0
  return Math.round(citations.reduce((sum, count) => sum + count, 0) / citations.length * 10) / 10
}

const getPatentPercentage = (cluster) => {
  const total = getClusterSize(cluster)
  if (total === 0) return 0
  return Math.round((getPatentCount(cluster) / total) * 100)
}

const getPaperPercentage = (cluster) => {
  const total = getClusterSize(cluster)
  if (total === 0) return 0
  return Math.round((getPaperCount(cluster) / total) * 100)
}

const getDocumentRatio = (cluster) => {
  const patentPct = getPatentPercentage(cluster)
  const paperPct = 100 - patentPct
  return `${patentPct}% Patents, ${paperPct}% Papers`
}

// Computed properties
const sortedClusters = computed(() => {
  if (!props.data?.clusters) return []
  return Object.entries(props.data.clusters)
    .sort(([,a], [,b]) => getClusterSize(b) - getClusterSize(a))
})

const citationSortedClusters = computed(() => {
  if (!props.data?.clusters) return []
  return Object.entries(props.data.clusters)
    .sort(([,a], [,b]) => getAvgCitations(b) - getAvgCitations(a))
})

const maxClusterSize = computed(() => {
  if (!props.data?.clusters) return 1
  return Math.max(...Object.values(props.data.clusters).map(c => getClusterSize(c))) || 1
})

const maxAvgCitations = computed(() => {
  if (!props.data?.clusters) return 1
  const max = Math.max(...Object.values(props.data.clusters).map(c => getAvgCitations(c)))
  return max > 0 ? max : 1
})

// Methods
const toggleClusterExpansion = (clusterId) => {
  expandedClusters.value[clusterId] = !expandedClusters.value[clusterId]
}

const getClusterDocuments = (cluster, clusterId) => {
  const docs = cluster?.documents || []
  const isExpanded = expandedClusters.value[clusterId]
  return isExpanded ? docs : docs.slice(0, 2)
}

const getAllKeywords = () => {
  if (!props.data?.clusters) return []
  
  const keywordCounts = {}
  
  Object.values(props.data.clusters).forEach(cluster => {
    (cluster.keywords || []).forEach(keyword => {
      keywordCounts[keyword] = (keywordCounts[keyword] || 0) + 1
    })
  })
  
  return Object.entries(keywordCounts)
    .map(([word, count]) => ({ word, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 20)
}

const getKeywordColor = (index) => {
  const colors = [
    'bg-blue-100 text-blue-800',
    'bg-green-100 text-green-800',
    'bg-purple-100 text-purple-800',
    'bg-yellow-100 text-yellow-800',
    'bg-pink-100 text-pink-800',
    'bg-indigo-100 text-indigo-800',
    'bg-red-100 text-red-800',
    'bg-gray-100 text-gray-800'
  ]
  return colors[index % colors.length]
}

const getKeywordSize = (count) => {
  const keywords = getAllKeywords()
  if (keywords.length === 0) return 12
  
  const maxCount = Math.max(...keywords.map(k => k.count))
  const minSize = 12
  const maxSize = 18
  return minSize + ((count / maxCount) * (maxSize - minSize))
}
</script>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>