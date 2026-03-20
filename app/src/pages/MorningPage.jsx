import { useState } from 'react'
import { useDaily } from '../hooks/useDaily'
import BottomNav from '../components/BottomNav'

function formatDate(dateStr) {
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString('ja-JP', { month: 'long', day: 'numeric', weekday: 'short' })
}

export default function MorningPage({ onNavigate }) {
  const {
    today,
    yesterday,
    combo,
    addTask,
    deleteTask,
  } = useDaily()

  const [inputValue, setInputValue] = useState('')

  const todayStr = new Date().toISOString().slice(0, 10)
  const tasks = today.topTasks || []
  const canAddTask = tasks.length < 3

  const yesterdayAchieved = yesterday
    ? (yesterday.topTasks || []).filter((t) => t.completed).length
    : 0
  const yesterdayTotal = yesterday ? (yesterday.topTasks || []).length : 0
  const hasYesterdayData = yesterday && yesterdayTotal > 0

  function handleAdd() {
    if (!inputValue.trim() || !canAddTask) return
    addTask(inputValue)
    setInputValue('')
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter') handleAdd()
  }

  const canStart = tasks.length > 0

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <div className="max-w-xl mx-auto px-4 pt-8 space-y-5">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-800">おはようございます</h1>
          <p className="text-sm text-gray-400 mt-0.5">{formatDate(todayStr)}</p>
        </div>

        {/* Combo badge */}
        {combo.currentStreak > 0 && (
          <div className="inline-flex items-center gap-2 bg-orange-50 border border-orange-200 rounded-full px-4 py-2">
            <span className="text-lg">🔥</span>
            <span className="text-sm font-semibold text-orange-600">
              {combo.currentStreak}日連続！
            </span>
            <span className="text-xs text-orange-400">合計 {combo.totalPoints}pts</span>
          </div>
        )}

        {/* Yesterday's summary */}
        {hasYesterdayData && (
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
              昨日のサマリー
            </h2>
            <div className="flex gap-4">
              <div className="flex-1 text-center bg-indigo-50 rounded-xl py-3">
                <div className="text-2xl font-bold text-indigo-600">
                  {yesterdayAchieved}/{yesterdayTotal}
                </div>
                <div className="text-xs text-gray-400 mt-0.5">タスク達成</div>
              </div>
              <div className="flex-1 text-center bg-red-50 rounded-xl py-3">
                <div className="text-2xl font-bold text-red-400">
                  {yesterday.pomodoroCount || 0}
                </div>
                <div className="text-xs text-gray-400 mt-0.5">ポモドーロ</div>
              </div>
              <div className="flex-1 text-center bg-amber-50 rounded-xl py-3">
                <div className="text-2xl font-bold text-amber-500">
                  {yesterday.points || 0}
                </div>
                <div className="text-xs text-gray-400 mt-0.5">pts獲得</div>
              </div>
            </div>
          </div>
        )}

        {/* Top 3 tasks */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
          <h2 className="text-base font-semibold text-gray-800 mb-1">今日のトップ3タスク</h2>
          <p className="text-xs text-gray-400 mb-4">最大3つまで設定できます</p>

          {tasks.length === 0 && (
            <p className="text-sm text-gray-300 text-center py-4">タスクを追加しましょう</p>
          )}

          <div className="space-y-2 mb-4">
            {tasks.map((task, index) => (
              <div
                key={task.id}
                className="flex items-center gap-3 bg-gray-50 rounded-xl px-4 py-3"
              >
                <span className="text-xs font-bold text-indigo-400 w-4 flex-shrink-0">
                  {index + 1}
                </span>
                <span className="flex-1 text-sm text-gray-700">{task.title}</span>
                <button
                  onClick={() => deleteTask(task.id)}
                  className="text-gray-300 hover:text-red-400 text-lg leading-none flex-shrink-0"
                >
                  ×
                </button>
              </div>
            ))}
          </div>

          {/* Input */}
          <div className="flex gap-2">
            <input
              className="flex-1 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 disabled:bg-gray-50 disabled:text-gray-300"
              placeholder={canAddTask ? 'タスクを入力...' : '3つ設定済み'}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={!canAddTask}
            />
            <button
              onClick={handleAdd}
              disabled={!canAddTask || !inputValue.trim()}
              className="bg-indigo-500 text-white px-4 py-2.5 rounded-xl text-sm font-medium hover:bg-indigo-600 disabled:opacity-40 disabled:cursor-not-allowed flex-shrink-0"
            >
              追加
            </button>
          </div>
        </div>

        {/* Start button */}
        <button
          onClick={() => onNavigate('work')}
          disabled={!canStart}
          className="w-full bg-indigo-500 text-white font-semibold py-4 rounded-2xl text-base hover:bg-indigo-600 shadow-md disabled:opacity-40 disabled:cursor-not-allowed transition-all"
        >
          作業を始める →
        </button>
      </div>

      <BottomNav current="morning" onNavigate={onNavigate} />
    </div>
  )
}
