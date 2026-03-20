import { useDaily } from '../hooks/useDaily'
import BottomNav from '../components/BottomNav'

export default function StatsPage({ onNavigate }) {
  const { combo, getWeekStats } = useDaily()
  const weekStats = getWeekStats()

  const totalPoints = combo.totalPoints || 0
  const currentStreak = combo.currentStreak || 0

  const totalPomodorosWeek = weekStats.reduce((sum, d) => {
    // pomodoroCount is on the day object; weekStats only has points/achieved/total
    // We recalculate from allDays via getWeekStats which we extended above
    return sum
  }, 0)

  // Max achieved rate for scaling bars (avoid division by zero)
  const maxRate = weekStats.reduce((max, d) => {
    if (d.total === 0) return max
    const rate = d.achieved / d.total
    return rate > max ? rate : max
  }, 0) || 1

  const today = new Date().toISOString().slice(0, 10)

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <div className="max-w-xl mx-auto px-4 pt-8 space-y-5">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-800">週次レポート</h1>
          <p className="text-sm text-gray-400 mt-0.5">直近7日間の記録</p>
        </div>

        {/* Summary stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-4 text-center">
            <div className="text-3xl font-bold text-amber-500">{totalPoints}</div>
            <div className="text-xs text-gray-400 mt-1">合計ポイント</div>
          </div>
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-4 text-center">
            <div className="text-3xl font-bold text-orange-500 flex items-center justify-center gap-1">
              <span>🔥</span>
              <span>{currentStreak}</span>
            </div>
            <div className="text-xs text-gray-400 mt-1">連続日数</div>
          </div>
        </div>

        {/* Bar chart */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
          <h2 className="text-base font-semibold text-gray-800 mb-5">タスク達成率（直近7日）</h2>
          <div className="flex items-end justify-between gap-2 h-32">
            {weekStats.map((d) => {
              const rate = d.total > 0 ? d.achieved / d.total : 0
              const heightPct = d.total > 0 ? Math.max(4, Math.round((rate / maxRate) * 100)) : 4
              const isToday = d.date === today
              const isEmpty = d.total === 0

              return (
                <div key={d.date} className="flex-1 flex flex-col items-center gap-1">
                  {/* Bar */}
                  <div className="w-full flex items-end justify-center" style={{ height: '100px' }}>
                    <div
                      className={`w-full rounded-t-lg transition-all ${
                        isEmpty
                          ? 'bg-gray-100'
                          : isToday
                          ? 'bg-indigo-500'
                          : rate >= 1
                          ? 'bg-green-400'
                          : rate > 0
                          ? 'bg-indigo-300'
                          : 'bg-gray-200'
                      }`}
                      style={{ height: `${heightPct}%` }}
                    />
                  </div>
                  {/* Label */}
                  <div className={`text-xs font-medium ${isToday ? 'text-indigo-600' : 'text-gray-400'}`}>
                    {d.label}
                  </div>
                  {/* Percentage */}
                  <div className="text-xs text-gray-400">
                    {d.total > 0 ? `${Math.round(rate * 100)}%` : '-'}
                  </div>
                </div>
              )
            })}
          </div>
          <div className="flex items-center gap-4 mt-4 text-xs text-gray-400">
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded-sm bg-indigo-500 inline-block" /> 今日
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded-sm bg-green-400 inline-block" /> 100%達成
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded-sm bg-indigo-300 inline-block" /> 部分達成
            </span>
          </div>
        </div>

        {/* Day-by-day list */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
          <h2 className="text-base font-semibold text-gray-800 mb-3">日別詳細</h2>
          <div className="divide-y divide-gray-50">
            {[...weekStats].reverse().map((d) => {
              const isToday = d.date === today
              const rate = d.total > 0 ? Math.round((d.achieved / d.total) * 100) : null

              return (
                <div
                  key={d.date}
                  className={`flex items-center gap-3 py-3 ${isToday ? 'text-indigo-700' : 'text-gray-700'}`}
                >
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${
                    isToday ? 'bg-indigo-100 text-indigo-600' : 'bg-gray-100 text-gray-400'
                  }`}>
                    {d.label}
                  </div>
                  <div className="flex-1">
                    <div className="text-xs text-gray-400">{d.date}</div>
                    <div className="text-sm font-medium mt-0.5">
                      {d.total > 0 ? (
                        <>
                          {d.achieved}/{d.total} タスク達成
                          {rate !== null && (
                            <span className={`ml-2 text-xs ${rate === 100 ? 'text-green-500' : 'text-gray-400'}`}>
                              ({rate}%)
                            </span>
                          )}
                        </>
                      ) : (
                        <span className="text-gray-300">データなし</span>
                      )}
                    </div>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <div className="text-sm font-bold text-amber-500">
                      {d.points > 0 ? `+${d.points}` : d.total > 0 ? '0' : '-'}
                    </div>
                    <div className="text-xs text-gray-400">pts</div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      <BottomNav current="stats" onNavigate={onNavigate} />
    </div>
  )
}
