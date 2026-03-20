import { useState } from 'react'
import GoalListPage from './pages/GoalListPage'
import MilestonePage from './pages/MilestonePage'

export default function App() {
  const [selectedGoalId, setSelectedGoalId] = useState(null)

  if (selectedGoalId) {
    return (
      <MilestonePage
        goalId={selectedGoalId}
        onBack={() => setSelectedGoalId(null)}
      />
    )
  }

  return <GoalListPage onSelectGoal={setSelectedGoalId} />
}
