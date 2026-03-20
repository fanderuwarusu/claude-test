import { useState } from 'react'
import { useGoals, getWeekRange, formatWeekLabel, isCurrentWeek, isPastWeek } from '../hooks/useGoals'

// Returns the ISO string of Monday N weeks from today (n=0 → this week, n=1 → next week …)
function weekOffset(n) {
  const { weekStart } = getWeekRange(new Date())
  const d = new Date(weekStart)
  d.setDate(d.getDate() + n * 7)
  return d.toISOString().slice(0, 10)
}

// ---- New Milestone Modal ----

function NewMilestoneModal({ onClose, onSave }) {
  const [title, setTitle] = useState('')
  const [weekStart, setWeekStart] = useState(weekOffset(0))

  function handleSubmit(e) {
    e.preventDefault()
    if (!title.trim() || !weekStart) return
    onSave({ title: title.trim(), weekStart })
    onClose()
  }

  // Pre-fill quick-select buttons: this week + next 7 weeks
  const quickWeeks = Array.from({ length: 8 }, (_, i) => ({
    value: weekOffset(i),
    label: i === 0 ? '今週' : i === 1 ? '来週' : `+${i}週`,
  }))

  return (
    <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">週次マイルストーンを追加</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">マイルストーン *</label>
            <input
              className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
              placeholder="例: 単語帳 Unit 1〜5 を完了する"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              autoFocus
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-2">対象週</label>
            <div className="flex flex-wrap gap-2 mb-3">
              {quickWeeks.map((w) => (
                <button
                  type="button"
                  key={w.value}
                  onClick={() => setWeekStart(w.value)}
                  className={`text-xs px-3 py-1.5 rounded-lg border transition-colors ${
                    weekStart === w.value
                      ? 'bg-indigo-500 text-white border-indigo-500'
                      : 'bg-white text-gray-500 border-gray-200 hover:border-indigo-300'
                  }`}
                >
                  {w.label}
                </button>
              ))}
            </div>
            <input
              type="date"
              className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
              value={weekStart}
              onChange={(e) => setWeekStart(e.target.value)}
            />
            {weekStart && (
              <p className="text-xs text-gray-400 mt-1">
                {formatWeekLabel(new Date(weekStart).toISOString())}
              </p>
            )}
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

// ---- Milestone Row ----

function MilestoneRow({ milestone, onReview, onDelete }) {
  const current = isCurrentWeek(milestone.weekStart)
  const past = isPastWeek(milestone.weekStart)
  const needsReview = past && !milestone.completed && milestone.reviewNote === ''

  return (
    <div
      className={`rounded-xl border p-4 flex gap-3 items-start transition-colors ${
        current
          ? 'border-indigo-200 bg-indigo-50'
          : milestone.completed
          ? 'border-green-100 bg-green-50'
          : needsReview
          ? 'border-amber-200 bg-amber-50'
          : 'border-gray-100 bg-white'
      }`}
    >
      {/* Status circle */}
      <div className="flex-shrink-0 mt-0.5">
        {milestone.completed ? (
          <div className="w-5 h-5 rounded-full bg-green-400 flex items-center justify-center">
            <span className="text-white text-xs">✓</span>
          </div>
        ) : past ? (
          <div className="w-5 h-5 rounded-full bg-amber-300 flex items-center justify-center">
            <span className="text-white text-xs">!</span>
          </div>
        ) : current ? (
          <div className="w-5 h-5 rounded-full border-2 border-indigo-400 bg-white" />
        ) : (
          <div className="w-5 h-5 rounded-full border-2 border-gray-200 bg-white" />
        )}
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className={`text-sm font-medium ${milestone.completed ? 'text-green-700 line-through' : 'text-gray-700'}`}>
            {milestone.title}
          </span>
          {current && <span className="text-xs bg-indigo-100 text-indigo-600 px-1.5 py-0.5 rounded-full">今週</span>}
          {needsReview && <span className="text-xs bg-amber-100 text-amber-600 px-1.5 py-0.5 rounded-full">振り返り待ち</span>}
        </div>
        <p className="text-xs text-gray-400 mt-0.5">{formatWeekLabel(milestone.weekStart)}</p>
        {milestone.reviewNote && (
          <p className="text-xs text-gray-500 mt-1 italic">"{milestone.reviewNote}"</p>
        )}
      </div>

      <div className="flex gap-1 flex-shrink-0">
        {(current || past) && (
          <button
            onClick={() => onReview(milestone)}
            className={`text-xs px-2.5 py-1 rounded-lg font-medium ${
              current ? 'bg-indigo-500 text-white hover:bg-indigo-600' : 'bg-amber-100 text-amber-700 hover:bg-amber-200'
            }`}
          >
            {milestone.completed ? '編集' : '振り返る'}
          </button>
        )}
        <button
          onClick={() => onDelete(milestone.id)}
          className="text-gray-300 hover:text-red-400 text-base px-1"
        >
          ×
        </button>
      </div>
    </div>
  )
}

// ---- Weekly Review Modal ----

function ReviewModal({ milestone, goalId, onClose }) {
  const { reviewMilestone } = useGoals()
  const [completed, setCompleted] = useState(milestone.completed)
  const [note, setNote] = useState(milestone.reviewNote || '')

  function handleSave() {
    reviewMilestone(goalId, milestone.id, { completed, reviewNote: note })
    onClose()
  }

  return (
    <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-1">週次振り返り</h2>
        <p className="text-sm text-gray-400 mb-4">{milestone.title}</p>

        <p className="text-xs text-gray-500 mb-2">{formatWeekLabel(milestone.weekStart)}</p>

        {/* Achieved? */}
        <div className="mb-4">
          <p className="text-sm font-medium text-gray-700 mb-2">このマイルストーンを達成できましたか？</p>
          <div className="flex gap-3">
            <button
              onClick={() => setCompleted(true)}
              className={`flex-1 py-3 rounded-xl border text-sm font-medium transition-colors ${
                completed
                  ? 'bg-green-500 border-green-500 text-white'
                  : 'border-gray-200 text-gray-500 hover:border-green-300'
              }`}
            >
              ✓ 達成した
            </button>
            <button
              onClick={() => setCompleted(false)}
              className={`flex-1 py-3 rounded-xl border text-sm font-medium transition-colors ${
                !completed
                  ? 'bg-red-400 border-red-400 text-white'
                  : 'border-gray-200 text-gray-500 hover:border-red-300'
              }`}
            >
              × 未達成
            </button>
          </div>
        </div>

        {/* Note */}
        <div className="mb-5">
          <label className="block text-sm font-medium text-gray-600 mb-1">
            振り返りメモ（任意）
          </label>
          <textarea
            className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 resize-none"
            rows={3}
            placeholder={completed ? '何がうまくいったか...' : '何が障害になったか、次週に向けて...'}
            value={note}
            onChange={(e) => setNote(e.target.value)}
          />
        </div>

        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 py-2.5 rounded-xl border border-gray-200 text-sm text-gray-500 hover:bg-gray-50"
          >
            キャンセル
          </button>
          <button
            onClick={handleSave}
            className="flex-1 py-2.5 rounded-xl bg-indigo-500 text-white text-sm font-medium hover:bg-indigo-600"
          >
            保存する
          </button>
        </div>
      </div>
    </div>
  )
}

// ---- Page ----

export default function MilestonePage({ goalId, onBack }) {
  const { goals, addMilestone, deleteMilestone } = useGoals()
  const [showAdd, setShowAdd] = useState(false)
  const [reviewTarget, setReviewTarget] = useState(null)

  const goal = goals.find((g) => g.id === goalId)
  if (!goal) return null

  const milestones = goal.milestones

  // Group by status for display
  const currentWeek = milestones.filter((m) => isCurrentWeek(m.weekStart))
  const upcoming = milestones.filter((m) => !isCurrentWeek(m.weekStart) && !isPastWeek(m.weekStart))
  const past = milestones.filter((m) => isPastWeek(m.weekStart)).sort((a, b) => b.weekStart.localeCompare(a.weekStart))

  const totalDone = milestones.filter((m) => m.completed).length
  const pct = milestones.length ? Math.round((totalDone / milestones.length) * 100) : 0

  return (
    <div className="min-h-screen bg-gray-50 px-4 py-8 max-w-xl mx-auto">
      {/* Header */}
      <button onClick={onBack} className="text-sm text-gray-400 hover:text-gray-600 mb-4 flex items-center gap-1">
        ← 目標一覧に戻る
      </button>

      <div className="bg-white rounded-2xl border border-gray-100 p-5 shadow-sm mb-6">
        <h1 className="text-xl font-bold text-gray-800">{goal.title}</h1>
        {goal.description && <p className="text-sm text-gray-400 mt-1">{goal.description}</p>}
        {goal.targetDate && (
          <p className="text-xs text-gray-400 mt-1">期限: {new Date(goal.targetDate).toLocaleDateString('ja-JP')}</p>
        )}
        {milestones.length > 0 && (
          <div className="mt-3">
            <div className="flex justify-between text-xs text-gray-400 mb-1">
              <span>{totalDone}/{milestones.length} 達成</span>
              <span>{pct}%</span>
            </div>
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
              <div className="h-full bg-indigo-400 rounded-full transition-all" style={{ width: `${pct}%` }} />
            </div>
          </div>
        )}
      </div>

      {/* Add button */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-base font-semibold text-gray-700">週次マイルストーン</h2>
        <button
          onClick={() => setShowAdd(true)}
          className="bg-indigo-500 text-white text-sm font-medium px-4 py-2 rounded-xl hover:bg-indigo-600 shadow-sm"
        >
          + 追加
        </button>
      </div>

      {milestones.length === 0 ? (
        <div className="text-center py-16 text-gray-300">
          <div className="text-4xl mb-2">📅</div>
          <p className="text-sm">マイルストーンがありません</p>
          <p className="text-xs mt-1">右上から週ごとの目標を追加しよう</p>
        </div>
      ) : (
        <div className="space-y-6">
          {currentWeek.length > 0 && (
            <section>
              <p className="text-xs font-semibold text-indigo-500 uppercase tracking-wide mb-2">今週</p>
              <div className="space-y-2">
                {currentWeek.map((m) => (
                  <MilestoneRow
                    key={m.id}
                    milestone={m}
                    onReview={setReviewTarget}
                    onDelete={(id) => deleteMilestone(goal.id, id)}
                  />
                ))}
              </div>
            </section>
          )}

          {upcoming.length > 0 && (
            <section>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">今後の予定</p>
              <div className="space-y-2">
                {upcoming.map((m) => (
                  <MilestoneRow
                    key={m.id}
                    milestone={m}
                    onReview={setReviewTarget}
                    onDelete={(id) => deleteMilestone(goal.id, id)}
                  />
                ))}
              </div>
            </section>
          )}

          {past.length > 0 && (
            <section>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">過去の週</p>
              <div className="space-y-2">
                {past.map((m) => (
                  <MilestoneRow
                    key={m.id}
                    milestone={m}
                    onReview={setReviewTarget}
                    onDelete={(id) => deleteMilestone(goal.id, id)}
                  />
                ))}
              </div>
            </section>
          )}
        </div>
      )}

      {showAdd && (
        <NewMilestoneModal
          onClose={() => setShowAdd(false)}
          onSave={(data) => addMilestone(goal.id, data)}
        />
      )}

      {reviewTarget && (
        <ReviewModal
          milestone={reviewTarget}
          goalId={goal.id}
          onClose={() => setReviewTarget(null)}
        />
      )}
    </div>
  )
}
