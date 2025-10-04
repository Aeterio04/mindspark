import { useState } from 'react'

import ConveyorSequencingDashboard from './components/ConveyorSequencingDashboard'

function App() {
  const [count, setCount] = useState(0)

  return (
    <ConveyorSequencingDashboard/>
  )
}

export default App
