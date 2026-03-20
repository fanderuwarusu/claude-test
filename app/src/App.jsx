import { useState } from 'react'
import MorningPage from './pages/MorningPage'
import WorkPage from './pages/WorkPage'
import EveningPage from './pages/EveningPage'
import StatsPage from './pages/StatsPage'
import GoalListPage from './pages/GoalListPage'
import MilestonePage from './pages/MilestonePage'
import BottomNav from './components/BottomNav'

export default function App() {
  const [screen, setScreen] = useState('morning')
  const [selectedGoalId, setSelectedGoalId] = useState(null)

  function handleNavigate(s) {
    setScreen(s)
    if (s !== 'goals') {
      setSelectedGoalId(null)
    }
  }

  if (screen === 'goals') {
    if (selectedGoalId) {
      // MilestonePage has its own back button, no bottom nav needed
      return (
        <>
          <div className="pb-16">
            <MilestonePage
              goalId={selectedGoalId}
              onBack={() => setSelectedGoalId(null)}
            />
          </div>
          <BottomNav current="goals" onNavigate={handleNavigate} />
        </>
      )
    }
    return (
      <>
        <div className="pb-16">
          <GoalListPage
            onSelectGoal={setSelectedGoalId}
          />
        </div>
        <BottomNav current="goals" onNavigate={handleNavigate} />
      </>
    )
  }

  if (screen === 'work') return <WorkPage onNavigate={handleNavigate} />
  if (screen === 'evening') return <EveningPage onNavigate={handleNavigate} />
  if (screen === 'stats') return <StatsPage onNavigate={handleNavigate} />

  return <MorningPage onNavigate={handleNavigate} />
}
