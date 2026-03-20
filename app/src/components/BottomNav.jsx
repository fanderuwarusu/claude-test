const TABS = [
  { id: 'morning', label: '朝', emoji: '☀️' },
  { id: 'work', label: '作業', emoji: '⏱️' },
  { id: 'evening', label: '夜', emoji: '🌙' },
  { id: 'stats', label: '統計', emoji: '📊' },
  { id: 'goals', label: '目標', emoji: '🎯' },
]

export default function BottomNav({ current, onNavigate }) {
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 z-40">
      <div className="max-w-xl mx-auto flex">
        {TABS.map((tab) => {
          const isActive = current === tab.id
          return (
            <button
              key={tab.id}
              onClick={() => onNavigate(tab.id)}
              className={`flex-1 flex flex-col items-center justify-center py-2.5 gap-0.5 transition-colors ${
                isActive ? 'text-indigo-600' : 'text-gray-400 hover:text-gray-600'
              }`}
            >
              <span className="text-lg leading-none">{tab.emoji}</span>
              <span className={`text-xs font-medium ${isActive ? 'text-indigo-600' : ''}`}>
                {tab.label}
              </span>
              {isActive && (
                <span className="absolute bottom-0 w-8 h-0.5 bg-indigo-500 rounded-t-full" />
              )}
            </button>
          )
        })}
      </div>
    </nav>
  )
}
