import { useState, useEffect, useCallback } from 'react'
import { useDaily } from '../hooks/useDaily'
import { usePomodoro, POMODORO_STATE } from '../hooks/usePomodoro'
import BottomNav from '../components/BottomNav'

function formatTime(seconds) {
  const m = Math.floor(seconds / 60).toString().padStart(2, '0')
  const s = (seconds % 60).toString().padStart(2, '0')
  return `${m}:${s}`
}

function FlashMessage({ message }) {
  if (!message) return null
  return (
    <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-indigo-500 text-white text-xs font-bold px-3 py-1 rounded-full shadow-md animate-bounce whitespace-nowrap">
      {message}
    </div>
  )
}

export default function WorkPage({ onNavigate }) {
  const { today, combo, toggleTask, logPomodoro } = useDaily()
  const [pomodoroFlash, setPomodoroFlash] = useState(false)
  const [taskFlash, setTaskFlash] = useState(null) // taskId

  const handleFocusComplete = useCallback(() => {
    logPomodoro()
    setPomodoroFlash(true)
    setTimeout(() => setPomodoroFlash(false), 2000)
  }, [logPomodoro])

  const { state, secondsLeft, start, pause, reset, isRunning } = usePomodoro({
    onComplete: handleFocusComplete,
  })

  const tasks = today.topTasks || []
  const pomodoroCount = today.pomodoroCount || 0

  const totalFocusSeconds = 25 * 60
  const progress = state === POMODORO_STATE.FOCUS
    ? (totalFocusSeconds - secondsLeft) / totalFocusSeconds
    : state === POMODORO_STATE.BREAK
    ? (5 * 60 - secondsLeft) / (5 * 60)
    : 0

  const circumference = 2 * Math.PI * 54
  const strokeDashoffset = circumference * (1 - progress)

  function stateLabel() {
    if (state === POMODORO_STATE.FOCUS) return '集中中'
    if (state === POMODORO_STATE.BREAK) return '休憩中'
    return 'スタート準備'
  }

  function stateColor() {
    if (state === POMODORO_STATE.FOCUS) return 'text-indigo-600'
    if (state === POMODORO_STATE.BREAK) return 'text-green-500'
    return 'text-gray-400'
  }

  function handleToggleTask(taskId) {
    toggleTask(taskId)
    const task = tasks.find((t) => t.id === taskId)
    if (task && !task.completed) {
      // About to be completed
      setTaskFlash(taskId)
      setTimeout(() => setTaskFlash(null), 2000)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <div className="max-w-xl mx-auto px-4 pt-8 space-y-5">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-800">集中タイム</h1>
          <p className="text-sm text-gray-400 mt-0.5">ポモドーロで集中しよう</p>
        </div>

        {/* Pomodoro Timer */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 flex flex-col items-center">
          {/* Circle */}
          <div className="relative mb-4">
            <svg width="140" height="140" className="-rotate-90">
              <circle
                cx="70"
                cy="70"
                r="54"
                fill="none"
                stroke="#f3f4f6"
                strokeWidth="8"
              />
              <circle
                cx="70"
                cy="70"
                r="54"
                fill="none"
                stroke={state === POMODORO_STATE.BREAK ? '#22c55e' : '#6366f1'}
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                style={{ transition: 'stroke-dashoffset 1s linear' }}
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-3xl font-bold text-gray-800 tabular-nums">
                {formatTime(secondsLeft)}
              </span>
            </div>
          </div>

          {/* State label */}
          <p className={`text-sm font-semibold mb-1 ${stateColor()}`}>{stateLabel()}</p>

          {/* Pomodoro flash */}
          {pomodoroFlash && (
            <div className="bg-green-100 text-green-700 text-sm font-bold px-4 py-2 rounded-full mb-3 animate-pulse">
              お疲れ様！ +5pts
            </div>
          )}

          {/* Pomodoro count */}
          <p className="text-sm text-gray-400 mb-5">
            🍅 今日: {pomodoroCount}回
          </p>

          {/* Controls */}
          <div className="flex gap-3 w-full max-w-xs">
            {!isRunning ? (
              <button
                onClick={start}
                className="flex-1 bg-indigo-500 text-white font-semibold py-3 rounded-xl hover:bg-indigo-600 text-sm"
              >
                {state === POMODORO_STATE.IDLE ? 'スタート' : '再開'}
              </button>
            ) : (
              <button
                onClick={pause}
                className="flex-1 bg-amber-400 text-white font-semibold py-3 rounded-xl hover:bg-amber-500 text-sm"
              >
                一時停止
              </button>
            )}
            <button
              onClick={reset}
              className="px-4 py-3 rounded-xl border border-gray-200 text-gray-400 hover:bg-gray-50 text-sm"
            >
              リセット
            </button>
          </div>
        </div>

        {/* Task list */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-gray-800">今日のタスク</h2>
            {combo.currentStreak >= 2 && (
              <span className="text-sm font-bold text-orange-500">
                🔥 コンボ ×{combo.currentStreak}
              </span>
            )}
          </div>

          {tasks.length === 0 ? (
            <p className="text-sm text-gray-300 text-center py-4">
              朝画面でタスクを設定してください
            </p>
          ) : (
            <div className="space-y-3">
              {tasks.map((task) => (
                <div
                  key={task.id}
                  className="flex items-center gap-3"
                >
                  <div className="relative flex-shrink-0">
                    <button
                      onClick={() => handleToggleTask(task.id)}
                      className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors ${
                        task.completed
                          ? 'bg-indigo-500 border-indigo-500'
                          : 'border-gray-300 hover:border-indigo-400'
                      }`}
                    >
                      {task.completed && (
                        <span className="text-white text-xs font-bold">✓</span>
                      )}
                    </button>
                    {taskFlash === task.id && (
                      <div className="absolute -top-7 left-1/2 -translate-x-1/2 bg-indigo-500 text-white text-xs font-bold px-2 py-0.5 rounded-full shadow-md whitespace-nowrap">
                        +10pts
                      </div>
                    )}
                  </div>
                  <span
                    className={`flex-1 text-sm transition-all ${
                      task.completed
                        ? 'text-gray-300 line-through'
                        : 'text-gray-700'
                    }`}
                  >
                    {task.title}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <BottomNav current="work" onNavigate={onNavigate} />
    </div>
  )
}
