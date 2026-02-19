import { useState, FormEvent } from 'react'

interface Business {
  place_id: string
  name: string
  address: string
  rating: number | null
  website: string | null
  matched_on: string
  matched_text: string
  relevance_score: number
}

// Mock data for when backend is unavailable
const MOCK_BUSINESSES: Business[] = [
  {
    place_id: 'mock_1',
    name: 'Brew & Bytes Coffee',
    address: '123 Queen St W, Toronto, ON',
    rating: 4.5,
    website: 'https://brewandbytes.com',
    matched_on: 'review',
    matched_text: 'Great wifi and plenty of power outlets. Perfect spot for remote work with excellent coffee.',
    relevance_score: 95.2
  },
  {
    place_id: 'mock_2',
    name: 'Tech Cafe Downtown',
    address: '456 King St E, Toronto, ON',
    rating: 4.7,
    website: 'https://techcafe.ca',
    matched_on: 'review',
    matched_text: 'Fast internet, quiet atmosphere, and comfortable seating. Laptop-friendly with great espresso.',
    relevance_score: 92.8
  },
  {
    place_id: 'mock_3',
    name: 'The Study Lounge',
    address: '789 Bloor St W, Toronto, ON',
    rating: 4.3,
    website: null,
    matched_on: 'description',
    matched_text: 'Coffee shop designed for students and remote workers with free high-speed wifi.',
    relevance_score: 89.5
  },
  {
    place_id: 'mock_4',
    name: 'Espresso & Code',
    address: '321 Yonge St, Toronto, ON',
    rating: 4.6,
    website: 'https://espressoandcode.com',
    matched_on: 'review',
    matched_text: 'Developer-friendly cafe with standing desks and blazing fast wifi. Great cold brew too!',
    relevance_score: 94.1
  },
  {
    place_id: 'mock_5',
    name: 'Caffeine Terminal',
    address: '654 Dundas St W, Toronto, ON',
    rating: 4.4,
    website: 'https://caffeineterminal.ca',
    matched_on: 'review',
    matched_text: 'Tech-themed coffee shop with excellent connectivity and a productive vibe.',
    relevance_score: 88.7
  },
  {
    place_id: 'mock_6',
    name: 'The Digital Grind',
    address: '987 College St, Toronto, ON',
    rating: 4.2,
    website: null,
    matched_on: 'review',
    matched_text: 'Quiet workspace with reliable wifi and fresh pastries. Lots of regulars working on laptops.',
    relevance_score: 87.3
  },
  {
    place_id: 'mock_7',
    name: 'Java Junction',
    address: '147 Spadina Ave, Toronto, ON',
    rating: 4.8,
    website: 'https://javajunction.ca',
    matched_on: 'review',
    matched_text: 'Amazing wifi speed, comfortable chairs, and the best lattes in town. Work-friendly environment.',
    relevance_score: 96.4
  },
  {
    place_id: 'mock_8',
    name: 'Pixel & Pour',
    address: '258 Queen St E, Toronto, ON',
    rating: 4.5,
    website: 'https://pixelandpour.com',
    matched_on: 'description',
    matched_text: 'Modern coffee shop catering to creatives and tech workers with fast internet and great coffee.',
    relevance_score: 90.2
  },
  {
    place_id: 'mock_9',
    name: 'Remote Workers Haven',
    address: '369 Harbord St, Toronto, ON',
    rating: 4.7,
    website: 'https://remotehaven.ca',
    matched_on: 'review',
    matched_text: 'Specifically designed for remote work with meeting rooms, printing services, and excellent wifi.',
    relevance_score: 97.1
  },
  {
    place_id: 'mock_10',
    name: 'Code & Coffee Co.',
    address: '741 Bathurst St, Toronto, ON',
    rating: 4.3,
    website: null,
    matched_on: 'review',
    matched_text: 'Programmer-friendly spot with multiple monitors allowed, fast wifi, and specialty coffee drinks.',
    relevance_score: 91.6
  }
]

function App() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<Business[]>([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [usingMockData, setUsingMockData] = useState(false)

  const handleSearch = async (e: FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setSearched(true)
    setUsingMockData(false)

    try {
      const res = await fetch(`http://localhost:8000/search?q=${encodeURIComponent(query)}&limit=20`, {
        signal: AbortSignal.timeout(3000)
      })
      const data = await res.json()
      setResults(data.results)
    } catch (error) {
      console.warn('Backend unavailable, using mock data:', error)
      setResults(MOCK_BUSINESSES)
      setUsingMockData(true)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Toronto Business Search
          </h1>
          <p className="text-gray-600">
            AI-powered semantic search across 2,000+ local businesses
          </p>
        </div>

        {/* Mock Data Warning */}
        {usingMockData && (
          <div className="mb-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p className="text-yellow-800 text-sm">
              ⚠️ <strong>Demo Mode:</strong> Backend service is unavailable. Showing mock data for demonstration purposes.
            </p>
          </div>
        )}

        {/* Search Bar */}
        <form onSubmit={handleSearch} className="mb-8">
          <div className="flex gap-3">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Try: 'coffee shop with good wifi for working' or 'pet store selling organic food'"
              className="flex-1 px-6 py-4 text-lg border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              disabled={loading}
              className="px-8 py-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </form>

        {/* Loading Spinner */}
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
            <p className="mt-4 text-gray-600">Searching businesses...</p>
          </div>
        )}

        {/* Empty State */}
        {!loading && searched && results.length === 0 && (
          <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
            <p className="text-gray-600">No businesses found for "{query}"</p>
            <p className="text-sm text-gray-500 mt-2">Try a different search term</p>
          </div>
        )}

        {/* Results Table */}
        {!loading && results.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <p className="text-sm text-gray-600">
                Found {results.length} businesses matching "{query}"
              </p>
            </div>
            
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Business Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Address
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Rating
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Match
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Matched Text
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Website
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {results.map((business) => (
                    <tr key={business.place_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {business.name}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-600 max-w-xs">
                          {business.address}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {business.rating ? (
                          <div className="flex items-center gap-1">
                            <span className="text-yellow-500">★</span>
                            <span className="text-sm font-semibold text-gray-900">
                              {business.rating.toFixed(1)}
                            </span>
                          </div>
                        ) : (
                          <span className="text-sm text-gray-400">N/A</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex flex-col gap-1">
                          
                          <span className="text-xs text-gray-500">
                            {business.relevance_score}%
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-600 max-w-md italic">
                          "{business.matched_text.substring(0, 100)}..."
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {business.website ? (
                          
                          <a
                            href={business.website}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-800 font-medium"
                            >
                          
                            {business.name}
                          </a>
                        ) : (
                          <span className="text-gray-400">N/A</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </main>
  )
}

export default App