import { ExternalLink } from 'lucide-react'

export const ScanResult = ({ scanResult }) => {
  if (!scanResult) return null

  const handleVisitSite = () => {
    if (scanResult.url && !scanResult.is_suspicious) {
      window.open(scanResult.url, '_blank', 'noopener,noreferrer')
    }
  }

  return (
    <div className={`mb-8 p-6 rounded-2xl max-w-2xl w-full flex items-start gap-4 transition-all animate-in fade-in slide-in-from-bottom-4 duration-500 ${scanResult.is_suspicious ? 'bg-red-50 dark:bg-red-950/40 border border-red-100 dark:border-red-900 shadow-sm' : 'bg-green-50 dark:bg-green-950/40 border border-green-100 dark:border-green-900 shadow-sm'}`}>
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${scanResult.is_suspicious ? 'bg-red-100 dark:bg-red-900/50 text-red-600 dark:text-red-400' : 'bg-green-100 dark:bg-green-900/50 text-green-600 dark:text-green-400'}`}>
        {scanResult.is_suspicious ? (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
            <line x1="12" y1="9" x2="12" y2="13"></line>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
          </svg>
        ) : (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
            <polyline points="22 4 12 14.01 9 11.01"></polyline>
          </svg>
        )}
      </div>
      <div className="flex-1">
        <div className="flex items-start justify-between">
          <div>
            <h3 className={`font-bold text-lg ${scanResult.is_suspicious ? 'text-red-900 dark:text-red-200' : 'text-green-900 dark:text-green-200'}`}>
              {scanResult.is_suspicious ? 'Malicious Activity Detected' : 'URL Appears Safe'}
            </h3>
            <p className={`text-sm mb-3 ${scanResult.is_suspicious ? 'text-red-700 dark:text-red-400' : 'text-green-700 dark:text-green-400'}`}>
              Confidence: {(scanResult.confidence * 100).toFixed(1)}% | Verdict: {scanResult.verdict}
            </p>
          </div>
          
          {!scanResult.is_suspicious && (
            <button
              onClick={handleVisitSite}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-bold rounded-xl transition-all shadow-md active:scale-95 group"
            >
              Visit Site
              <ExternalLink size={14} className="group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
            </button>
          )}
        </div>

        <div className="flex flex-wrap gap-2 mt-2">
          {Object.entries(scanResult.predictions).map(([model, score]) => (
            <span key={model} className={`text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded-md ${score > 0.5 ? 'bg-red-200 dark:bg-red-900 text-red-800 dark:text-red-300' : 'bg-green-200 dark:bg-green-900 text-green-800 dark:text-green-300'}`}>
              {model}: {(score * 100).toFixed(0)}%
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}

