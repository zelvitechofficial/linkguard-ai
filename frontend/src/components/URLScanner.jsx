import { useUsage } from '../context/UsageContext'

export const URLScanner = ({ inputValue, setInputValue, isLoading, handleScan }) => {
  const { usage } = useUsage()

  return (
    <div className="input-container mb-8 bg-white dark:bg-[#1e293b] border border-gray-200 dark:border-gray-700/50">
      <input
        type="url"
        className="flex-1 w-full bg-transparent border-none outline-none focus:outline-none focus:border-transparent focus:ring-0 text-lg placeholder-gray-400 dark:placeholder-gray-500 text-gray-900 dark:text-gray-100 h-12 px-4"
        placeholder="Enter URL to analyze (e.g. https://example.com)"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        disabled={isLoading}
        onKeyDown={(e) => e.key === 'Enter' && inputValue && !isLoading && handleScan()}
      />
      <button 
        onClick={() => handleScan()}
        disabled={isLoading || !inputValue}
        className={`w-12 h-12 shrink-0 flex items-center justify-center rounded-[24px] transition-all ${isLoading || !inputValue ? 'bg-gray-200 dark:bg-gray-700 text-gray-400 dark:text-gray-500' : 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-md hover:shadow-lg'}`}
      >
        {isLoading ? (
          <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
        ) : (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
            <line x1="5" y1="12" x2="19" y2="12"></line>
            <polyline points="12 5 19 12 12 19"></polyline>
          </svg>
        )}
      </button>
      <div className="absolute -bottom-6 left-4 text-[11px] font-medium text-gray-400 dark:text-gray-500 tracking-wider uppercase">
        Usage: {usage.scans.used} / {usage.scans.limit} Scans
      </div>
    </div>
  )
}

