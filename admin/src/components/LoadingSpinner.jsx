import { Loader2 } from 'lucide-react';

export default function LoadingSpinner({ message = 'Loading...' }) {
  return (
    <div className="flex flex-col items-center justify-center h-64 w-full">
      <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
      {message && <p className="mt-4 text-sm text-gray-500 dark:text-gray-400 font-medium">{message}</p>}
    </div>
  );
}
