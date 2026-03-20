import { useState, useEffect, useRef, useCallback } from 'react'

const FOCUS_SECONDS = 25 * 60
const BREAK_SECONDS = 5 * 60

export const POMODORO_STATE = {
  IDLE: 'IDLE',
  FOCUS: 'FOCUS',
  BREAK: 'BREAK',
}

export function usePomodoro({ onComplete } = {}) {
  const [state, setState] = useState(POMODORO_STATE.IDLE)
  const [secondsLeft, setSecondsLeft] = useState(FOCUS_SECONDS)
  const [isRunning, setIsRunning] = useState(false)
  const onCompleteRef = useRef(onComplete)

  useEffect(() => {
    onCompleteRef.current = onComplete
  }, [onComplete])

  useEffect(() => {
    if (!isRunning) return

    const interval = setInterval(() => {
      setSecondsLeft((prev) => {
        if (prev <= 1) {
          clearInterval(interval)
          setIsRunning(false)

          if (state === POMODORO_STATE.FOCUS) {
            // Focus session complete
            if (onCompleteRef.current) onCompleteRef.current()
            setState(POMODORO_STATE.BREAK)
            setSecondsLeft(BREAK_SECONDS)
          } else if (state === POMODORO_STATE.BREAK) {
            setState(POMODORO_STATE.IDLE)
            setSecondsLeft(FOCUS_SECONDS)
          }

          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(interval)
  }, [isRunning, state])

  const start = useCallback(() => {
    if (state === POMODORO_STATE.IDLE) {
      setState(POMODORO_STATE.FOCUS)
      setSecondsLeft(FOCUS_SECONDS)
    }
    setIsRunning(true)
  }, [state])

  const pause = useCallback(() => {
    setIsRunning(false)
  }, [])

  const reset = useCallback(() => {
    setIsRunning(false)
    setState(POMODORO_STATE.IDLE)
    setSecondsLeft(FOCUS_SECONDS)
  }, [])

  return {
    state,
    secondsLeft,
    start,
    pause,
    reset,
    isRunning,
  }
}
