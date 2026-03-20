import { useState } from 'react'
import { useDaily } from '../hooks/useDaily'
import BottomNav from '../components/BottomNav'

function formatDate(dateStr) {
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString('ja-JP', { month: 'long', day: 'numeric', weekday: 'short' })
}

export default function EveningPage({ onNavigate }) {
  const { today, saveDiary, saveNextDayPlan } = useDaily()

  const todayStr = new Date().toISOString().slice(0, 10)
  const tasks = today.topTasks || []
  const achieved = tasks.filter((t) => t.completed).length
  const total = tasks.length

  const [diaryText, setDiaryText] = useState(today.diary || '')
  const [diarySaved, setDiarySaved] = useState(false)

  const [planInputs, setPlanInputs] = useState(
    today.nextDayPlan
      ? [...today.nextDayPlan, '', '', ''].slice(0, 3)
      : ['', '', '']
  )
  const [planSaved, setPlanSaved] = useState(false)

  function handleSaveDiary() {
    saveDiary(diaryText)
    setDiarySaved(true)
    setTimeout(() => setDiarySaved(false), 2000)
  }

  function handleSavePlan() {
    const filtered = planInputs.map((s) => s.trim()).filter(Boolean)
    saveNextDayPlan(filtered)
    setPlanSaved(true)
    setTimeout(() => setPlanSaved(false), 2000)
  }

  function updatePlanInput(index, value) {
    setPlanInputs((prev) => {
      const next = [...prev]
      next[index] = value
      return next
    })
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <div className="max-w-xl mx-auto px-4 pt-8 space-y-5">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-800">今日の振り返り</h1>
          <p className="text-sm text-gray-400 mt-0.5">{formatDate(todayStr)}</p>
        </div>

        {/* Summary */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
            今日のまとめ
          </h2>
          <div className="flex gap-4">
            <div className="flex-1 text-center bg-indigo-50 rounded-xl py-3">
              <div className="text-2xl font-bold text-indigo-600">
                {achieved}/{total}
              </div>
              <div className="text-xs text-gray-400 mt-0.5">タスク達成</div>
            </div>
            <div className="flex-1 text-center bg-red-50 rounded-xl py-3">
              <div className="text-2xl font-bold text-red-400">
                {today.pomodoroCount || 0}
              </div>
              <div className="text-xs text-gray-400 mt-0.5">ポモドーロ</div>
            </div>
            <div className="flex-1 text-center bg-amber-50 rounded-xl py-3">
              <div className="text-2xl font-bold text-amber-500">
                {today.points || 0}
              </div>
              <div className="text-xs text-gray-400 mt-0.5">pts獲得</div>
            </div>
          </div>
        </div>

        {/* Task list (read-only) */}
        {tasks.length > 0 && (
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
            <h2 className="text-base font-semibold text-gray-800 mb-3">タスク結果</h2>
            <div className="space-y-2">
              {tasks.map((task) => (
                <div
                  key={task.id}
                  className={`flex items-center gap-3 rounded-xl px-4 py-3 ${
                    task.completed ? 'bg-green-50' : 'bg-gray-50'
                  }`}
                >
                  <span className={`text-base flex-shrink-0 ${task.completed ? 'text-green-500' : 'text-red-400'}`}>
                    {task.completed ? '✓' : '✗'}
                  </span>
                  <span
                    className={`flex-1 text-sm ${
                      task.completed ? 'text-green-700 line-through' : 'text-gray-500'
                    }`}
                  >
                    {task.title}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Diary */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
          <h2 className="text-base font-semibold text-gray-800 mb-1">日記</h2>
          <p className="text-xs text-gray-400 mb-3">今日の感想や気づきを書いてみよう</p>
          <textarea
            className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 resize-none text-gray-700"
            rows={5}
            placeholder="今日はどんな一日でしたか？"
            value={diaryText}
            onChange={(e) => setDiaryText(e.target.value)}
          />
          <div className="flex items-center justify-between mt-3">
            {diarySaved && (
              <span className="text-xs text-green-600 font-medium">保存しました ✓</span>
            )}
            {!diarySaved && <span />}
            <button
              onClick={handleSaveDiary}
              className="bg-indigo-500 text-white text-sm font-medium px-5 py-2 rounded-xl hover:bg-indigo-600"
            >
              保存する
            </button>
          </div>
        </div>

        {/* Next day plan */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
          <h2 className="text-base font-semibold text-gray-800 mb-1">明日のプラン</h2>
          <p className="text-xs text-gray-400 mb-3">明日やりたいタスクを最大3つ入力</p>
          <div className="space-y-2 mb-4">
            {planInputs.map((val, index) => (
              <div key={index} className="flex items-center gap-3">
                <span className="text-xs font-bold text-indigo-400 w-4 flex-shrink-0">
                  {index + 1}
                </span>
                <input
                  className="flex-1 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
                  placeholder={`タスク ${index + 1}（任意）`}
                  value={val}
                  onChange={(e) => updatePlanInput(index, e.target.value)}
                />
              </div>
            ))}
          </div>
          <div className="flex items-center justify-between">
            {planSaved && (
              <span className="text-xs text-green-600 font-medium">保存しました ✓</span>
            )}
            {!planSaved && <span />}
            <button
              onClick={handleSavePlan}
              className="bg-indigo-500 text-white text-sm font-medium px-5 py-2 rounded-xl hover:bg-indigo-600"
            >
              保存する
            </button>
          </div>
        </div>

        {/* Stats link */}
        <button
          onClick={() => onNavigate('stats')}
          className="w-full bg-white border border-gray-200 text-gray-700 font-medium py-3.5 rounded-2xl text-sm hover:bg-gray-50 shadow-sm flex items-center justify-center gap-2"
        >
          <span>📊</span>
          <span>週次レポートを見る</span>
        </button>
      </div>

      <BottomNav current="evening" onNavigate={onNavigate} />
    </div>
  )
}
