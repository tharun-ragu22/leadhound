import { useState, type SyntheticEvent } from 'react'

interface Business {
  place_id: string
  business_name: string
  address: string
  phone_number: string | null
  website: string | null
  reason: string
}

// Mock data for when backend is unavailable
const MOCK_BUSINESSES: Business[] = [
  {
    place_id: 'mock_1',
    business_name: 'Brew & Bytes Coffee',
    address: '123 Queen St W, Toronto, ON',
    phone_number: '647',
    website: 'https://brewandbytes.com',
    reason: 'why not',
  },
  {
    place_id: 'mock_2',
    business_name: 'Brew & Bytes Coffee',
    address: '123 Queen St W, Toronto, ON',
    phone_number: '647',
    website: 'https://brewandbytes.com',
    reason: 'why not',
  },
  {
    place_id: 'mock_3',
    business_name: 'The Study Lounge',
    address: '123 Queen St W, Toronto, ON',
    phone_number: '647',
    website: 'https://brewandbytes.com',
    reason: 'why not',
  },
]

function App() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<Business[]>([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [usingMockData, setUsingMockData] = useState(false)

  const handleSearch = async (e: SyntheticEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setSearched(true)
    setUsingMockData(false)

    try {
      const request_body = {
        query_string: query
      }
      const res = await fetch(`https://business-search-812254520874.us-central1.run.app/query`, {
        method: 'POST',
        signal: AbortSignal.timeout(1000000),
        headers: {
          'Content-Type': 'application/json', // This tells FastAPI to parse the body as JSON
        },
        body: JSON.stringify(request_body)
      })
      const data = await res.json()
      setResults(data.res)
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
              placeholder="Try: 'coffee shop with good wifi for working'"
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
                      Phone Number
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Website
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Reason
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {results.map((business) => (
                    <tr key={business.place_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {business.business_name}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-600 max-w-xs">
                          {business.address}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-600 max-w-xs">
                          {business.phone_number}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-600 max-w-xs">
                          <a href={business.website ?? "/"}>Link</a>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-600 max-w-md italic">
                          {business.reason}
                        </div>
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