import { useState, useEffect } from 'react'

const STORAGE_KEY = 'motivflow_goals'

// Derive the Monday and Sunday of the week containing `date`
export function getWeekRange(date) {
  const d = new Date(date)
  const day = d.getDay() // 0=Sun … 6=Sat
  const diffToMon = (day === 0 ? -6 : 1 - day)
  const mon = new Date(d)
  mon.setDate(d.getDate() + diffToMon)
  mon.setHours(0, 0, 0, 0)
  const sun = new Date(mon)
  sun.setDate(mon.getDate() + 6)
  sun.setHours(23, 59, 59, 999)
  return { weekStart: mon.toISOString(), weekEnd: sun.toISOString() }
}

export function formatWeekLabel(weekStart) {
  const d = new Date(weekStart)
  const sun = new Date(d)
  sun.setDate(d.getDate() + 6)
  const fmt = (dt) =>
    dt.toLocaleDateString('ja-JP', { month: 'short', day: 'numeric' })
  return `${fmt(d)} 〜 ${fmt(sun)}`
}

export function isCurrentWeek(weekStart) {
  const { weekStart: curStart } = getWeekRange(new Date())
  return weekStart.slice(0, 10) === curStart.slice(0, 10)
}

export function isPastWeek(weekStart) {
  const { weekStart: curStart } = getWeekRange(new Date())
  return weekStart < curStart
}

function load() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function save(goals) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(goals))
}

export function useGoals() {
  const [goals, setGoals] = useState(load)

  useEffect(() => {
    save(goals)
  }, [goals])

  // ---------- Goal CRUD ----------
  function addGoal({ title, description, targetDate }) {
    const goal = {
      id: crypto.randomUUID(),
      title,
      description,
      targetDate: targetDate || null,
      createdAt: new Date().toISOString(),
      milestones: [],
    }
    setGoals((prev) => [...prev, goal])
    return goal.id
  }

  function deleteGoal(goalId) {
    setGoals((prev) => prev.filter((g) => g.id !== goalId))
  }

  // ---------- Milestone CRUD ----------
  function addMilestone(goalId, { title, weekStart }) {
    const { weekEnd } = getWeekRange(weekStart)
    const milestone = {
      id: crypto.randomUUID(),
      goalId,
      title,
      weekStart: new Date(weekStart).toISOString(),
      weekEnd,
      completed: false,
      completedAt: null,
      reviewNote: '',
    }
    setGoals((prev) =>
      prev.map((g) =>
        g.id === goalId
          ? { ...g, milestones: [...g.milestones, milestone].sort((a, b) => a.weekStart.localeCompare(b.weekStart)) }
          : g
      )
    )
    return milestone.id
  }

  function deleteMilestone(goalId, milestoneId) {
    setGoals((prev) =>
      prev.map((g) =>
        g.id === goalId
          ? { ...g, milestones: g.milestones.filter((m) => m.id !== milestoneId) }
          : g
      )
    )
  }

  // ---------- Weekly Review ----------
  function reviewMilestone(goalId, milestoneId, { completed, reviewNote }) {
    setGoals((prev) =>
      prev.map((g) =>
        g.id === goalId
          ? {
              ...g,
              milestones: g.milestones.map((m) =>
                m.id === milestoneId
                  ? {
                      ...m,
                      completed,
                      completedAt: completed ? new Date().toISOString() : null,
                      reviewNote: reviewNote ?? m.reviewNote,
                    }
                  : m
              ),
            }
          : g
      )
    )
  }

  return { goals, addGoal, deleteGoal, addMilestone, deleteMilestone, reviewMilestone }
}
