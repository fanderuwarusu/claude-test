import { useState } from 'react'
import { useGoals, isPastWeek, isCurrentWeek, formatWeekLabel } from '../hooks/useGoals'

// ---- Small helpers ----

function Progress({ milestones }) {
  if (!milestones.length) return null
  const done = milestones.filter((m) => m.completed).length
  const pct = Math.round((done / milestones.length) * 100)
  return (
    <div className="mt-2">
      <div className="flex justify-between text-xs text-gray-400 mb-1">
        <span>{done}/{milestones.length} マイルストーン達成</span>
        <span>{pct}%</span>
      </div>
      <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
        <div
          className="h-full bg-indigo-400 rounded-full transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}

function WeekBadge({ weekStart }) {
  if (isCurrentWeek(weekStart))
    return <span className="text-xs bg-indigo-100 text-indigo-600 px-2 py-0.5 rounded-full font-medium">今週</span>
  if (isPastWeek(weekStart))
    return <span className="text-xs bg-gray-100 text-gray-400 px-2 py-0.5 rounded-full">過去</span>
  return <span className="text-xs bg-green-50 text-green-600 px-2 py-0.5 rounded-full">予定</span>
}

// ---- New Goal Modal ----

function NewGoalModal({ onClose, onSave }) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [targetDate, setTargetDate] = useState('')

  function handleSubmit(e) {
    e.preventDefault()
    if (!title.trim()) return
    onSave({ title: title.trim(), description: description.trim(), targetDate })
    onClose()
  }

  return (
    <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">長期目標を追加</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">目標タイトル *</label>
            <input
              className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
              placeholder="例: TOEIC 800点を取得する"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              autoFocus
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">詳細・背景（任意）</label>
            <textarea
              className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 resize-none"
              rows={3}
              placeholder="なぜこの目標を達成したいか..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">目標期限（任意）</label>
            <input
              type="date"
              className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
              value={targetDate}
              onChange={(e) => setTargetDate(e.target.value)}
            />
          </div>
          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2.5 rounded-xl border border-gray-200 text-sm text-gray-500 hover:bg-gray-50"
            >
              キャンセル
            </button>
            <button
              type="submit"
              className="flex-1 py-2.5 rounded-xl bg-indigo-500 text-white text-sm font-medium hover:bg-indigo-600"
            >
              追加する
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

// ---- Goal Card ----

function GoalCard({ goal, onSelect, onDelete }) {
  const currentMilestone = goal.milestones.find((m) => isCurrentWeek(m.weekStart))
  return (
    <div
      className="bg-white rounded-2xl border border-gray-100 p-5 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
      onClick={() => onSelect(goal.id)}
    >
      <div className="flex justify-between items-start gap-2">
        <h3 className="font-semibold text-gray-800 text-base leading-snug">{goal.title}</h3>
        <button
          onClick={(e) => { e.stopPropagation(); onDelete(goal.id) }}
          className="text-gray-300 hover:text-red-400 text-lg leading-none flex-shrink-0 mt-0.5"
        >
          ×
        </button>
      </div>
      {goal.description && (
        <p className="text-sm text-gray-400 mt-1 line-clamp-2">{goal.description}</p>
      )}
      {goal.targetDate && (
        <p className="text-xs text-gray-400 mt-1">期限: {new Date(goal.targetDate).toLocaleDateString('ja-JP')}</p>
      )}
      {currentMilestone && (
        <div className="mt-3 bg-indigo-50 rounded-xl px-3 py-2 text-sm">
          <span className="text-indigo-400 text-xs font-medium">今週のマイルストーン</span>
          <p className="text-indigo-700 font-medium mt-0.5">{currentMilestone.title}</p>
        </div>
      )}
      <Progress milestones={goal.milestones} />
    </div>
  )
}

// ---- Page ----

export default function GoalListPage({ onSelectGoal }) {
  const { goals, addGoal, deleteGoal } = useGoals()
  const [showModal, setShowModal] = useState(false)

  return (
    <div className="min-h-screen bg-gray-50 px-4 py-8 max-w-xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">長期目標</h1>
          <p className="text-sm text-gray-400 mt-0.5">目標を設定して週単位で進めよう</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="bg-indigo-500 text-white text-sm font-medium px-4 py-2 rounded-xl hover:bg-indigo-600 shadow-sm"
        >
          + 追加
        </button>
      </div>

      {goals.length === 0 ? (
        <div className="text-center py-20 text-gray-300">
          <div className="text-5xl mb-3">🎯</div>
          <p className="text-sm">まだ目標がありません</p>
          <p className="text-xs mt-1">右上のボタンから追加してみよう</p>
        </div>
      ) : (
        <div className="space-y-4">
          {goals.map((g) => (
            <GoalCard
              key={g.id}
              goal={g}
              onSelect={onSelectGoal}
              onDelete={deleteGoal}
            />
          ))}
        </div>
      )}

      {showModal && (
        <NewGoalModal
          onClose={() => setShowModal(false)}
          onSave={addGoal}
        />
      )}
    </div>
  )
}
