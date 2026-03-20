import { useState, useCallback } from 'react'

const STORAGE_KEY = 'motivflow_data'

const DAY_LABELS = ['日', '月', '火', '水', '木', '金', '土']

function getToday() {
  return new Date().toISOString().slice(0, 10)
}

function getYesterday() {
  const d = new Date()
  d.setDate(d.getDate() - 1)
  return d.toISOString().slice(0, 10)
}

function emptyDay() {
  return {
    topTasks: [],
    diary: '',
    pomodoroCount: 0,
    points: 0,
  }
}

function emptyCombo() {
  return {
    currentStreak: 0,
    lastActiveDate: '',
    totalPoints: 0,
  }
}

function load() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return { days: {}, combo: emptyCombo() }
    const parsed = JSON.parse(raw)
    return {
      days: parsed.days || {},
      combo: parsed.combo || emptyCombo(),
    }
  } catch {
    return { days: {}, combo: emptyCombo() }
  }
}

function save(data) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
}

export function useDaily() {
  const [data, setData] = useState(load)

  const today = data.days[getToday()] || emptyDay()
  const yesterday = data.days[getYesterday()] || null
  const allDays = data.days
  const combo = data.combo

  const updateData = useCallback((updater) => {
    setData((prev) => {
      const next = updater(prev)
      save(next)
      return next
    })
  }, [])

  function ensureToday(days) {
    const key = getToday()
    return {
      ...days,
      [key]: days[key] || emptyDay(),
    }
  }

  function addTask(title) {
    const trimmed = title.trim()
    if (!trimmed) return
    updateData((prev) => {
      const days = ensureToday(prev.days)
      const key = getToday()
      const current = days[key]
      if (current.topTasks.length >= 3) return prev
      const newTask = { id: crypto.randomUUID(), title: trimmed, completed: false }
      return {
        ...prev,
        days: {
          ...days,
          [key]: {
            ...current,
            topTasks: [...current.topTasks, newTask],
          },
        },
      }
    })
  }

  function toggleTask(taskId) {
    updateData((prev) => {
      const days = ensureToday(prev.days)
      const key = getToday()
      const yesterdayKey = getYesterday()
      const current = days[key]

      const updatedTasks = current.topTasks.map((t) =>
        t.id === taskId ? { ...t, completed: !t.completed } : t
      )
      const task = updatedTasks.find((t) => t.id === taskId)
      const isNowCompleted = task?.completed

      let pointsEarned = 0
      let newCombo = { ...prev.combo }

      if (isNowCompleted) {
        pointsEarned += 10

        // Combo logic
        const yesterdayData = days[yesterdayKey]
        const yesterdayActive = yesterdayData &&
          yesterdayData.topTasks.some((t) => t.completed)

        const lastActive = newCombo.lastActiveDate
        const todayStr = key

        if (lastActive === todayStr) {
          // Already counted today, just add combo bonus
          pointsEarned += 5 * newCombo.currentStreak
        } else {
          // New day activity
          if (yesterdayActive || lastActive === yesterdayKey) {
            newCombo.currentStreak = (newCombo.currentStreak || 0) + 1
          } else {
            newCombo.currentStreak = 1
          }
          newCombo.lastActiveDate = todayStr
          pointsEarned += 5 * newCombo.currentStreak
        }
        newCombo.totalPoints = (newCombo.totalPoints || 0) + pointsEarned
      } else {
        // Uncompleting a task: subtract the base points only (not combo)
        pointsEarned = -10
        newCombo.totalPoints = Math.max(0, (newCombo.totalPoints || 0) + pointsEarned)
      }

      const newPoints = Math.max(0, (current.points || 0) + pointsEarned)

      return {
        ...prev,
        combo: newCombo,
        days: {
          ...days,
          [key]: {
            ...current,
            topTasks: updatedTasks,
            points: newPoints,
          },
        },
      }
    })
  }

  function deleteTask(taskId) {
    updateData((prev) => {
      const days = ensureToday(prev.days)
      const key = getToday()
      const current = days[key]
      return {
        ...prev,
        days: {
          ...days,
          [key]: {
            ...current,
            topTasks: current.topTasks.filter((t) => t.id !== taskId),
          },
        },
      }
    })
  }

  function logPomodoro() {
    updateData((prev) => {
      const days = ensureToday(prev.days)
      const key = getToday()
      const current = days[key]
      const pointsEarned = 5
      return {
        ...prev,
        combo: {
          ...prev.combo,
          totalPoints: (prev.combo.totalPoints || 0) + pointsEarned,
        },
        days: {
          ...days,
          [key]: {
            ...current,
            pomodoroCount: (current.pomodoroCount || 0) + 1,
            points: (current.points || 0) + pointsEarned,
          },
        },
      }
    })
  }

  function saveDiary(text) {
    updateData((prev) => {
      const days = ensureToday(prev.days)
      const key = getToday()
      const current = days[key]
      return {
        ...prev,
        days: {
          ...days,
          [key]: {
            ...current,
            diary: text,
          },
        },
      }
    })
  }

  function saveNextDayPlan(tasks) {
    updateData((prev) => {
      const days = ensureToday(prev.days)
      const key = getToday()
      const current = days[key]
      return {
        ...prev,
        days: {
          ...days,
          [key]: {
            ...current,
            nextDayPlan: tasks,
          },
        },
      }
    })
  }

  function getWeekStats() {
    const result = []
    for (let i = 6; i >= 0; i--) {
      const d = new Date()
      d.setDate(d.getDate() - i)
      const dateStr = d.toISOString().slice(0, 10)
      const label = DAY_LABELS[d.getDay()]
      const dayData = data.days[dateStr]
      const total = dayData?.topTasks?.length || 0
      const achieved = dayData?.topTasks?.filter((t) => t.completed).length || 0
      const points = dayData?.points || 0
      result.push({ date: dateStr, label, achieved, total, points })
    }
    return result
  }

  return {
    today,
    yesterday,
    allDays,
    combo,
    addTask,
    toggleTask,
    deleteTask,
    logPomodoro,
    saveDiary,
    saveNextDayPlan,
    getWeekStats,
  }
}
