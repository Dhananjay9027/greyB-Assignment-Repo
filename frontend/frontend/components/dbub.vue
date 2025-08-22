<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Debug Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/vue/3.3.4/vue.global.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/axios/1.5.0/axios.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen">
    <div id="app" class="container mx-auto px-4 py-8">
        <!-- Header -->
        <div class="bg-white rounded-lg shadow-md p-6 mb-6">
            <h1 class="text-3xl font-bold text-gray-800 mb-2">🔧 API Debug Dashboard</h1>
            <p class="text-gray-600">Comprehensive testing tool for your Patent & Paper Search API</p>
        </div>

        <!-- Connection Status -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div class="bg-white rounded-lg shadow-md p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <h3 class="text-lg font-semibold text-gray-800">API Status</h3>
                        <p :class="statusColor" class="font-medium">{{ connectionStatus }}</p>
                    </div>
                    <div :class="statusIcon" class="text-2xl">{{ statusEmoji }}</div>
                </div>
                <button @click="checkHealth" 
                        class="mt-4 w-full bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded">
                    Check Health
                </button>
            </div>

            <div class="bg-white rounded-lg shadow-md p-6">
                <h3 class="text-lg font-semibold text-gray-800 mb-2">API Configuration</h3>
                <div class="space-y-2 text-sm">
                    <div><strong>URL:</strong> {{ apiUrl }}</div>
                    <div><strong>CORS:</strong> {{ corsStatus }}</div>
                    <div><strong>Timeout:</strong> {{ timeout }}ms</div>
                </div>
            </div>

            <div class="bg-white rounded-lg shadow-md p-6">
                <h3 class="text-lg font-semibold text-gray-800 mb-2">Last Response</h3>
                <div class="space-y-1 text-sm">
                    <div><strong>Status:</strong> <span :class="lastResponse.status >= 400 ? 'text-red-600' : 'text-green-600'">{{ lastResponse.status || 'N/A' }}</span></div>
                    <div><strong>Time:</strong> {{ lastResponse.time || 'N/A' }}ms</div>
                    <div><strong>Size:</strong> {{ lastResponse.size || 'N/A' }} bytes</div>
                </div>
            </div>
        </div>

        <!-- Network Diagnostics -->
        <div class="bg-white rounded-lg shadow-md p-6 mb-6">
            <h3 class="text-xl font-semibold text-gray-800 mb-4">🌐 Network Diagnostics</h3>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <h4 class="font-medium text-gray-700 mb-3">Connection Tests</h4>
                    <div class="space-y-2">
                        <button @click="testCORS" 
                                class="w-full bg-purple-500 hover:bg-purple-600 text-white py-2 px-4 rounded">
                            Test CORS
                        </button>
                        <button @click="testOptions" 
                                class="w-full bg-indigo-500 hover:bg-indigo-600 text-white py-2 px-4 rounded">
                            Test OPTIONS
                        </button>
                        <button @click="testPreflight" 
                                class="w-full bg-pink-500 hover:bg-pink-600 text-white py-2 px-4 rounded">
                            Test Preflight
                        </button>
                    </div>
                </div>

                <div>
                    <h4 class="font-medium text-gray-700 mb-3">Quick Endpoint Tests</h4>
                    <div class="space-y-2">
                        <button @click="testEndpoint('/')" 
                                class="w-full bg-green-500 hover:bg-green-600 text-white py-2 px-4 rounded">
                            Test Root (/)
                        </button>
                        <button @click="testEndpoint('/health')" 
                                class="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded">
                            Test Health
                        </button>
                        <button @click="testSearch()" 
                                class="w-full bg-orange-500 hover:bg-orange-600 text-white py-2 px-4 rounded">
                            Test Search
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Custom Search Test -->
        <div class="bg-white rounded-lg shadow-md p-6 mb-6">
            <h3 class="text-xl font-semibold text-gray-800 mb-4">🔍 Custom Search Test</h3>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Search Query</label>
                        <input v-model="searchParams.query" 
                               type="text" 
                               placeholder="artificial intelligence"
                               class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                    </div>
                    
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Year From</label>
                            <input v-model="searchParams.year_start" 
                                   type="number" 
                                   placeholder="2010"
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Year To</label>
                            <input v-model="searchParams.year_end" 
                                   type="number" 
                                   placeholder="2024"
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Document Type</label>
                            <select v-model="searchParams.doc_type" 
                                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                                <option value="both">Both</option>
                                <option value="patents">Patents</option>
                                <option value="papers">Papers</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Top K</label>
                            <input v-model="searchParams.top_k" 
                                   type="number" 
                                   placeholder="10"
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                        </div>
                    </div>

                    <button @click="performSearch" 
                            :disabled="isLoading"
                            class="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-medium py-3 px-4 rounded-md">
                        {{ isLoading ? 'Searching...' : 'Perform Search' }}
                    </button>
                </div>

                <div>
                    <h4 class="font-medium text-gray-700 mb-3">Request Preview</h4>
                    <pre class="bg-gray-100 p-3 rounded-md text-sm overflow-x-auto">{{ JSON.stringify(searchParams, null, 2) }}</pre>
                </div>
            </div>
        </div>

        <!-- Response/Error Log -->
        <div class="bg-white rounded-lg shadow-md p-6 mb-6">
            <h3 class="text-xl font-semibold text-gray-800 mb-4">📋 Response & Error Log</h3>
            
            <div class="space-y-4 max-h-96 overflow-y-auto">
                <div v-for="(log, index) in logs" :key="index"
                     :class="[
                       'p-4 rounded-md border-l-4',
                       log.type === 'success' ? 'bg-green-50 border-green-500' :
                       log.type === 'error' ? 'bg-red-50 border-red-500' :
                       log.type === 'warning' ? 'bg-yellow-50 border-yellow-500' :
                       'bg-blue-50 border-blue-500'
                     ]">
                    <div class="flex justify-between items-start mb-2">
                        <div class="flex items-center space-x-2">
                            <span class="text-lg">{{ log.emoji }}</span>
                            <span class="font-medium">{{ log.action }}</span>
                        </div>
                        <span class="text-sm text-gray-500">{{ log.timestamp }}</span>
                    </div>
                    
                    <div class="text-sm">
                        <div v-if="log.status"><strong>Status:</strong> {{ log.status }}</div>
                        <div v-if="log.message"><strong>Message:</strong> {{ log.message }}</div>
                        <div v-if="log.duration"><strong>Duration:</strong> {{ log.duration }}ms</div>
                        
                        <div v-if="log.data" class="mt-3">
                            <strong>Response Data:</strong>
                            <pre class="bg-gray-100 p-2 rounded mt-1 text-xs overflow-x-auto">{{ JSON.stringify(log.data, null, 2) }}</pre>
                        </div>
                    </div>
                </div>
                
                <div v-if="logs.length === 0" class="text-center text-gray-500 py-8">
                    No logs yet. Start testing to see results here.
                </div>
            </div>

            <button @click="clearLogs" 
                    class="mt-4 bg-red-500 hover:bg-red-600 text-white py-2 px-4 rounded">
                Clear Logs
            </button>
        </div>

        <!-- Browser Info -->
        <div class="bg-white rounded-lg shadow-md p-6">
            <h3 class="text-xl font-semibold text-gray-800 mb-4">🖥️ Browser Information</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
                <div>
                    <div><strong>User Agent:</strong> {{ browserInfo.userAgent }}</div>
                    <div><strong>Language:</strong> {{ browserInfo.language }}</div>
                    <div><strong>Platform:</strong> {{ browserInfo.platform }}</div>
                </div>
                <div>
                    <div><strong>Cookie Enabled:</strong> {{ browserInfo.cookieEnabled }}</div>
                    <div><strong>Online:</strong> {{ browserInfo.onLine }}</div>
                    <div><strong>Current URL:</strong> {{ browserInfo.currentUrl }}</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const { createApp } = Vue;
        
        createApp({
            data() {
                return {
                    apiUrl: 'http://localhost:8000',
                    timeout: 10000,
                    connectionStatus: 'Unknown',
                    corsStatus: 'Unknown',
                    isLoading: false,
                    lastResponse: {},
                    logs: [],
                    searchParams: {
                        query: 'artificial intelligence',
                        top_k: 10,
                        doc_type: 'both',
                        year_start: 2010,
                        year_end: 2024,
                        min_citations: null
                    },
                    browserInfo: {
                        userAgent: navigator.userAgent,
                        language: navigator.language,
                        platform: navigator.platform,
                        cookieEnabled: navigator.cookieEnabled,
                        onLine: navigator.onLine,
                        currentUrl: window.location.href
                    }
                }
            },
            
            computed: {
                statusColor() {
                    return {
                        'Connected': 'text-green-600',
                        'Disconnected': 'text-red-600',
                        'Unknown': 'text-yellow-600'
                    }[this.connectionStatus] || 'text-gray-600';
                },
                
                statusIcon() {
                    return {
                        'Connected': 'text-green-500',
                        'Disconnected': 'text-red-500',
                        'Unknown': 'text-yellow-500'
                    }[this.connectionStatus] || 'text-gray-500';
                },
                
                statusEmoji() {
                    return {
                        'Connected': '✅',
                        'Disconnected': '❌',
                        'Unknown': '⚠️'
                    }[this.connectionStatus] || '❓';
                }
            },

            mounted() {
                this.checkHealth();
                this.detectBrowserIssues();
            },

            methods: {
                addLog(type, action, data = null) {
                    this.logs.unshift({
                        type,
                        action,
                        timestamp: new Date().toLocaleTimeString(),
                        emoji: {
                            'success': '✅',
                            'error': '❌', 
                            'warning': '⚠️',
                            'info': 'ℹ️'
                        }[type],
                        ...data
                    });
                    
                    if (this.logs.length > 50) {
                        this.logs = this.logs.slice(0, 50);
                    }
                },

                async makeRequest(method, endpoint, data = null) {
                    const startTime = performance.now();
                    
                    try {
                        const config = {
                            method,
                            url: `${this.apiUrl}${endpoint}`,
                            timeout: this.timeout,
                            headers: {
                                'Content-Type': 'application/json',
                                'Accept': 'application/json'
                            }
                        };
                        
                        if (data) {
                            config.data = data;
                        }
                        
                        const response = await axios(config);
                        const duration = Math.round(performance.now() - startTime);
                        
                        this.lastResponse = {
                            status: response.status,
                            time: duration,
                            size: JSON.stringify(response.data).length
                        };
                        
                        return { success: true, response, duration };
                        
                    } catch (error) {
                        const duration = Math.round(performance.now() - startTime);
                        
                        this.lastResponse = {
                            status: error.response?.status || 'Error',
                            time: duration,
                            size: 0
                        };
                        
                        return { success: false, error, duration };
                    }
                },

                async checkHealth() {
                    this.isLoading = true;
                    
                    const result = await this.makeRequest('GET', '/health');
                    
                    if (result.success) {
                        this.connectionStatus = 'Connected';
                        this.corsStatus = 'Working';
                        this.addLog('success', 'Health Check', {
                            status: result.response.status,
                            message: 'API is healthy',
                            duration: result.duration,
                            data: result.response.data
                        });
                    } else {
                        this.connectionStatus = 'Disconnected';
                        this.addLog('error', 'Health Check Failed', {
                            status: result.error.response?.status,
                            message: result.error.message,
                            duration: result.duration
                        });
                    }
                    
                    this.isLoading = false;
                },

                async testCORS() {
                    const result = await this.makeRequest('GET', '/');
                    
                    if (result.success) {
                        const corsHeaders = result.response.headers['access-control-allow-origin'];
                        this.corsStatus = corsHeaders ? 'Enabled' : 'Limited';
                        
                        this.addLog('success', 'CORS Test', {
                            status: result.response.status,
                            message: `CORS headers: ${corsHeaders || 'None'}`,
                            duration: result.duration
                        });
                    } else {
                        this.addLog('error', 'CORS Test Failed', {
                            message: result.error.message,
                            duration: result.duration
                        });
                    }
                },

                async testOptions() {
                    const result = await this.makeRequest('OPTIONS', '/search');
                    
                    if (result.success) {
                        this.addLog('success', 'OPTIONS Test', {
                            status: result.response.status,
                            message: 'OPTIONS request successful',
                            duration: result.duration,
                            data: result.response.headers
                        });
                    } else {
                        this.addLog('error', 'OPTIONS Test Failed', {
                            message: result.error.message,
                            duration: result.duration
                        });
                    }
                },

                async testPreflight() {
                    try {
                        const response = await fetch(`${this.apiUrl}/search`, {
                            method: 'OPTIONS',
                            headers: {
                                'Access-Control-Request-Method': 'POST',
                                'Access-Control-Request-Headers': 'Content-Type'
                            }
                        });
                        
                        this.addLog('success', 'Preflight Test', {
                            status: response.status,
                            message: 'Preflight successful',
                            data: Object.fromEntries(response.headers.entries())
                        });
                    } catch (error) {
                        this.addLog('error', 'Preflight Test Failed', {
                            message: error.message
                        });
                    }
                },

                async testEndpoint(endpoint) {
                    const result = await this.makeRequest('GET', endpoint);
                    
                    if (result.success) {
                        this.addLog('success', `Test ${endpoint}`, {
                            status: result.response.status,
                            message: 'Endpoint accessible',
                            duration: result.duration,
                            data: result.response.data
                        });
                    } else {
                        this.addLog('error', `Test ${endpoint} Failed`, {
                            status: result.error.response?.status,
                            message: result.error.message,
                            duration: result.duration
                        });
                    }
                },

                async testSearch() {
                    const testPayload = {
                        query: "test",
                        top_k: 5,
                        doc_type: "both"
                    };
                    
                    const result = await this.makeRequest('POST', '/search', testPayload);
                    
                    if (result.success) {
                        this.addLog('success', 'Search Test', {
                            status: result.response.status,
                            message: `Found ${result.response.data.total_found} results`,
                            duration: result.duration,
                            data: result.response.data
                        });
                    } else {
                        this.addLog('error', 'Search Test Failed', {
                            status: result.error.response?.status,
                            message: result.error.message,
                            duration: result.duration
                        });
                    }
                },

                async performSearch() {
                    this.isLoading = true;
                    
                    const cleanParams = { ...this.searchParams };
                    if (!cleanParams.year_start) delete cleanParams.year_start;
                    if (!cleanParams.year_end) delete cleanParams.year_end;
                    if (!cleanParams.min_citations) delete cleanParams.min_citations;
                    
                    const result = await this.makeRequest('POST', '/search', cleanParams);
                    
                    if (result.success) {
                        this.addLog('success', 'Custom Search', {
                            status: result.response.status,
                            message: `Query: "${cleanParams.query}" - Found ${result.response.data.total_found} results`,
                            duration: result.duration,
                            data: result.response.data
                        });
                    } else {
                        this.addLog('error', 'Custom Search Failed', {
                            status: result.error.response?.status,
                            message: result.error.message,
                            duration: result.duration
                        });
                    }
                    
                    this.isLoading = false;
                },

                detectBrowserIssues() {
                    // Check for common issues
                    if (!window.fetch) {
                        this.addLog('warning', 'Browser Compatibility', {
                            message: 'Fetch API not supported'
                        });
                    }
                    
                    if (location.protocol === 'https:' && this.apiUrl.startsWith('http:')) {
                        this.addLog('warning', 'Mixed Content', {
                            message: 'HTTPS page trying to access HTTP API - this may be blocked'
                        });
                    }
                },

                clearLogs() {
                    this.logs = [];
                }
            }
        }).mount('#app');
    </script>
</body>
</html>