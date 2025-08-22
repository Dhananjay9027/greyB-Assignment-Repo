<template>
  <div class="space-y-6">
    <!-- Summary Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-blue-50 rounded-lg p-4">
        <div class="text-2xl font-bold text-blue-900">{{ data.summary.total_documents }}</div>
        <div class="text-blue-600 text-sm">Total Documents</div>
      </div>
      <div class="bg-green-50 rounded-lg p-4">
        <div class="text-2xl font-bold text-green-900">{{ data.summary.patents }}</div>
        <div class="text-green-600 text-sm">Patents</div>
      </div>
      <div class="bg-purple-50 rounded-lg p-4">
        <div class="text-2xl font-bold text-purple-900">{{ data.summary.papers }}</div>
        <div class="text-purple-600 text-sm">Research Papers</div>
      </div>
      <div class="bg-orange-50 rounded-lg p-4">
        <div class="text-2xl font-bold text-orange-900">{{ data.summary.clusters_analyzed }}</div>
        <div class="text-orange-600 text-sm">Sub-topics</div>
      </div>
    </div>

    <!-- Trend Heatmap -->
    <div class="bg-white rounded-lg border p-6">
      <h3 class="text-lg font-semibold mb-4">📈 Publication Trends by Sub-topic</h3>
      <div class="space-y-4">
        <div v-for="(cluster, clusterId) in data.trend_analysis" :key="clusterId"
             class="border border-gray-200 rounded-lg p-4">
          
          <!-- Cluster Header -->
          <div class="flex items-center justify-between mb-4">
            <div>
              <h4 class="font-medium text-gray-900">{{ cluster.cluster_name }}</h4>
              <div class="flex flex-wrap gap-1 mt-1">
                <span v-for="keyword in cluster.keywords.slice(0, 4)" :key="keyword"
                      class="px-2 py-1 bg-gray-100 text-gray-600 rounded-full text-xs">
                  {{ keyword }}
                </span>
              </div>
            </div>
            
            <!-- Trend Indicator -->
            <div class="text-right">
              <div :class="[
                'px-3 py-1 rounded-full text-sm font-medium',
                getTrendColor(cluster.trend_metrics.trend_status)
              ]">
                {{ getTrendIcon(cluster.trend_metrics.trend_status) }}
                {{ cluster.trend_metrics.trend_status.replace('_', ' ').toUpperCase() }}
              </div>
              <div class="text-xs text-gray-500 mt-1">
                {{ cluster.trend_metrics.velocity_percentage > 0 ? '+' : '' }}{{ cluster.trend_metrics.velocity_percentage }}%
              </div>
            </div>
          </div>

          <!-- Year Timeline -->
          <div class="mb-4">
            <div class="flex items-center justify-between text-sm text-gray-600 mb-2">
              <span>Publication Timeline</span>
              <span>{{ cluster.trend_metrics.year_span }}</span>
            </div>
            
            <!-- Timeline Bars -->
            <div class="flex items-end space-x-1 h-16 bg-gray-50 rounded p-2">
              <div v-for="(count, year) in cluster.yearly_data" :key="year"
                   class="flex-1 flex flex-col items-center">
                <div 
                  :style="{ height: getBarHeight(count.total, getMaxCount(cluster.yearly_data)) + '%' }"
                  :class="[
                    'w-full rounded-t transition-all duration-300 cursor-pointer',
                    getYearColor(year, Object.keys(cluster.yearly_data))
                  ]"
                  :title="`${year}: ${count.total} documents`">
                </div>
                <span class="text-xs text-gray-500 mt-1">{{ year }}</span>
              </div>
            </div>
          </div>

          <!-- Cluster Stats -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <div class="font-medium text-gray-900">{{ cluster.composition.size }}</div>
              <div class="text-gray-600">Total Docs</div>
            </div>
            <div>
              <div class="font-medium text-blue-900">{{ cluster.composition.patents }}</div>
              <div class="text-gray-600">Patents</div>
            </div>
            <div>
              <div class="font-medium text-green-900">{{ cluster.composition.papers }}</div>
              <div class="text-gray-600">Papers</div>
            </div>
            <div>
              <div class="font-medium text-purple-900">{{ cluster.composition.avg_citations }}</div>
              <div class="text-gray-600">Avg Citations</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Overall Trend Chart -->
    <div class="bg-white rounded-lg border p-6">
      <h3 class="text-lg font-semibold mb-4">📊 Overall Publication Velocity</h3>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        <!-- Velocity Chart -->
        <div>
          <h4 class="font-medium text-gray-700 mb-3">Growth Velocity by Sub-topic</h4>
          <div class="space-y-2">
            <div v-for="(cluster, clusterId) in data.trend_analysis" :key="clusterId"
                 class="flex items-center">
              <div class="w-32 text-sm text-gray-600 truncate">
                {{ cluster.cluster_name.split(':')[1]?.substring(0, 20) || `Topic ${parseInt(clusterId) + 1}` }}
              </div>
              <div class="flex-1 mx-3">
                <div class="bg-gray-200 rounded-full h-2">
                  <div 
                    :class="[
                      'h-2 rounded-full transition-all duration-500',
                      cluster.trend_metrics.velocity_percentage >= 0 ? 'bg-green-500' : 'bg-red-500'
                    ]"
                    :style="{ width: Math.abs(cluster.trend_metrics.velocity_percentage) + '%' }">
                  </div>
                </div>
              </div>
              <div class="w-16 text-right text-sm font-medium">
                {{ cluster.trend_metrics.velocity_percentage > 0 ? '+' : '' }}{{ cluster.trend_metrics.velocity_percentage }}%
              </div>
            </div>
          </div>
        </div>

        <!-- Document Type Distribution -->
        <div>
          <h4 class="font-medium text-gray-700 mb-3">Document Type Distribution</h4>
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <div class="w-4 h-4 bg-blue-500 rounded mr-2"></div>
                <span class="text-sm">Patents</span>
              </div>
              <span class="font-medium">{{ data.summary.patents }}</span>
            </div>
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <div class="w-4 h-4 bg-green-500 rounded mr-2"></div>
                <span class="text-sm">Research Papers</span>
              </div>
              <span class="font-medium">{{ data.summary.papers }}</span>
            </div>
          </div>
          
          <!-- Visual Distribution Bar -->
          <div class="mt-4 h-4 bg-gray-200 rounded-full overflow-hidden">
            <div class="h-full flex">
              <div 
                class="bg-blue-500"
                :style="{ width: (data.summary.patents / data.summary.total_documents * 100) + '%' }">
              </div>
              <div 
                class="bg-green-500"
                :style="{ width: (data.summary.papers / data.summary.total_documents * 100) + '%' }">
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Key Insights -->
    <div class="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6">
      <h3 class="text-lg font-semibold mb-4">💡 Key Insights</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <h4 class="font-medium text-gray-900 mb-2">Growing Topics</h4>
          <ul class="space-y-1 text-sm">
            <li v-for="cluster in getGrowingTopics()" :key="cluster.name"
                class="flex items-center text-green-700">
              <span class="mr-2">📈</span>
              {{ cluster.name.split(':')[1]?.trim() || cluster.name }}
              <span class="ml-auto font-medium">+{{ cluster.growth }}%</span>
            </li>
          </ul>
        </div>
        <div>
          <h4 class="font-medium text-gray-900 mb-2">Declining Topics</h4>
          <ul class="space-y-1 text-sm">
            <li v-for="cluster in getDecliningTopics()" :key="cluster.name"
                class="flex items-center text-red-700">
              <span class="mr-2">📉</span>
              {{ cluster.name.split(':')[1]?.trim() || cluster.name }}
              <span class="ml-auto font-medium">{{ cluster.growth }}%</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: {
    type: Object,
    required: true
  }
})

// Helper functions
const getTrendColor = (status) => {
  const colors = {
    growing: 'bg-green-100 text-green-800',
    declining: 'bg-red-100 text-red-800',
    stable: 'bg-yellow-100 text-yellow-800',
    insufficient_data: 'bg-gray-100 text-gray-800'
  }
  return colors[status] || colors.stable
}

const getTrendIcon = (status) => {
  const icons = {
    growing: '📈',
    declining: '📉',
    stable: '➡️',
    insufficient_data: '❓'
  }
  return icons[status] || '➡️'
}

const getMaxCount = (yearlyData) => {
  return Math.max(...Object.values(yearlyData).map(data => data.total))
}

const getBarHeight = (count, maxCount) => {
  return maxCount > 0 ? (count / maxCount) * 80 : 0
}

const getYearColor = (year, allYears) => {
  const sortedYears = allYears.sort()
  const index = sortedYears.indexOf(year.toString())
  const colors = [
    'bg-blue-300', 'bg-blue-400', 'bg-blue-500', 
    'bg-blue-600', 'bg-blue-700', 'bg-blue-800'
  ]
  return colors[Math.min(index, colors.length - 1)] || 'bg-blue-500'
}

const getGrowingTopics = () => {
  return Object.values(props.data.trend_analysis)
    .filter(cluster => cluster.trend_metrics.trend_status === 'growing')
    .map(cluster => ({
      name: cluster.cluster_name,
      growth: cluster.trend_metrics.velocity_percentage
    }))
    .sort((a, b) => b.growth - a.growth)
    .slice(0, 3)
}

const getDecliningTopics = () => {
  return Object.values(props.data.trend_analysis)
    .filter(cluster => cluster.trend_metrics.trend_status === 'declining')
    .map(cluster => ({
      name: cluster.cluster_name,
      growth: cluster.trend_metrics.velocity_percentage
    }))
    .sort((a, b) => a.growth - b.growth)
    .slice(0, 3)
}
</script>