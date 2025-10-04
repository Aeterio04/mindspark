import React, { useState, useEffect, useRef } from 'react';

const ConveyorSequencingDashboard = () => {
  const [systemState, setSystemState] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [simulationStatus, setSimulationStatus] = useState('stopped');
  const [processHistory, setProcessHistory] = useState([]);
  const websocket = useRef(null);

  // Color definitions
  const colorMap = {
    C1: { name: 'Red', color: '#EF4444' },
    C2: { name: 'Green', color: '#10B981' },
    C3: { name: 'Blue', color: '#3B82F6' },
    C4: { name: 'Yellow', color: '#EAB308' },
    C5: { name: 'Orange', color: '#F97316' },
    C6: { name: 'Purple', color: '#A855F7' },
    C7: { name: 'Pink', color: '#EC4899' },
    C8: { name: 'Brown', color: '#92400E' },
    C9: { name: 'Cyan', color: '#06B6D4' },
    C10: { name: 'Magenta', color: '#D946EF' },
    C11: { name: 'Lime', color: '#84CC16' },
    C12: { name: 'Gray', color: '#9CA3AF' },
    0: { name: 'Empty', color: '#374151' }
  };

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (websocket.current) {
        websocket.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    try {
      const ws = new WebSocket('ws://localhost:8000/ws');
      websocket.current = ws;

      ws.onopen = () => {
        console.log('✅ Connected to backend');
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          console.log("data:", message.data);
          if (message.type === 'system_update') {
            console.log('📦 Received data:', message.data);
            setSystemState(message.data);

            // if (message.data.process_flow?.recent_operations) {
            //   setProcessHistory(prev => [
            //     ...message.data.process_flow.recent_operations.slice(-10),
            //     ...prev.slice(0, 20)
            //   ]);
            // }
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onclose = () => {
        console.log('❌ Disconnected from backend');
        setIsConnected(false);
        setSimulationStatus('stopped');

        setTimeout(() => {
          console.log('🔄 Attempting to reconnect...');
          connectWebSocket();
        }, 3000);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    } catch (error) {
      console.error('Error creating WebSocket:', error);
    }
  };

  const startSimulation = () => {
    if (websocket.current && websocket.current.readyState === WebSocket.OPEN) {
      websocket.current.send(JSON.stringify({ type: 'start_simulation' }));
      setSimulationStatus('running');
      console.log('🚀 Starting simulation...');
    } else {
      console.error('WebSocket not connected');
      setIsConnected(false);
    }
  };

  const stopSimulation = () => {
    if (websocket.current && websocket.current.readyState === WebSocket.OPEN) {
      websocket.current.send(JSON.stringify({ type: 'stop_simulation' }));
      setSimulationStatus('stopped');
      console.log('⏹️ Stopping simulation...');
    }
  };

  const resetSystem = () => {
    if (websocket.current && websocket.current.readyState === WebSocket.OPEN) {
      websocket.current.send(JSON.stringify({ type: 'reset_system' }));
      setProcessHistory([]);
      console.log('🔄 Resetting system...');
    }
  };

  // Vehicle Icon Component
  const VehicleIcon = ({ color = '#9CA3AF', size = 'normal' }) => {
    const sizes = {
      small: 'w-4 h-4',
      normal: 'w-6 h-6',
      large: 'w-8 h-8'
    };

    return (
      <div className={`${sizes[size]}`}>
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M8 16C8 17.1046 7.10457 18 6 18C4.89543 18 4 17.1046 4 16C4 14.8954 4.89543 14 6 14C7.10457 14 8 14.8954 8 16Z" fill={color} />
          <path d="M20 16C20 17.1046 19.1046 18 18 18C16.8954 18 16 17.1046 16 16C16 14.8954 16.8954 14 18 14C19.1046 14 20 14.8954 20 16Z" fill={color} />
          <path d="M3 11L5 6H19L21 11M3 11V16H4M3 11H21M21 11V16H20M4 16H16M20 16H16M16 16V14" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill={color} fillOpacity="0.8" />
        </svg>
      </div>
    );
  };

  // Conveyor Belt Sequence Component
  const ConveyorBeltSequence = ({ sequence = [], currentColor, stats = {} }) => {
    console.log('Conveyor sequence:', sequence);
    console.log('Current color:', currentColor);

    return (
      <div className="bg-gradient-to-r from-gray-800 to-gray-700 rounded-lg p-3 border-2 border-gray-600">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-white font-bold text-xl">Conveyor Belt Sequence</h3>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3 bg-gray-900 rounded-lg px-4 py-2">
              <div
                className="w-6 h-6 rounded-full border-2 border-white shadow-lg"
                style={{ backgroundColor: currentColor ? colorMap[currentColor]?.color : '#6B7280' }}
              ></div>
              <div>
                <div className="text-white font-semibold text-sm">Current Color</div>
                <div className="text-gray-300 text-xs">{currentColor || 'None'}</div>
              </div>
            </div>
            <div className="bg-yellow-600 rounded-lg px-4 py-2">
              <div className="text-white font-bold text-sm">Changes: {stats.color_changes || 0}</div>
            </div>
          </div>
        </div>

        <div className="relative bg-gray-900 rounded-xl p-4 border-2 border-gray-700 mb-4">
          <div className="absolute top-1/2 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-yellow-500 to-transparent transform -translate-y-1/2"></div>

          <div className="flex space-x-4 overflow-x-auto pb-4 pt-4 min-h-24 items-center">
            {sequence && sequence.length > 0 ? (
              sequence.map((color, idx) => (
                <div key={idx} className="flex flex-col items-center">
                  <div className="relative">
                    <VehicleIcon color={colorMap[color]?.color || '#FFFFF'} size="large" />
                    {idx === sequence.length - 1 && (
                      <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full "></div>
                    )}
                  </div>
                  <div className="mt-2 text-xs text-gray-400 bg-gray-800 px-2 py-1 rounded">
                    {color}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-gray-500 text-lg italic flex items-center justify-center w-full ">
                No cars processed yet. Start simulation to see the sequence.
              </div>
            )}
          </div>
        </div>

        {sequence && sequence.length > 0 && (
          <div className="text-center text-gray-400 text-sm">
            Showing last {sequence.length} cars
          </div>
        )}
      </div>
    );
  };

  // Process Flow Component
  const RealTimeProcessFlow = ({ processHistory = [] }) => (
    <div className="bg-gradient-to-r from-purple-800 to-purple-900 rounded-lg p-6 border-2 border-purple-600">
      <h3 className="text-white font-bold text-xl mb-6">Real-time Process Flow</h3>

      <div className="overflow-x-auto pb-4">
        <div className="flex space-x-4 min-w-max">
          {processHistory.slice(0, 10).map((process, index) => (
            <div key={index} className="flex-shrink-0 bg-gray-900 rounded-xl p-4 border border-gray-700 min-w-64">
              <div className="flex justify-between items-start mb-3">
                <span className={`px-3 py-1 rounded-full text-xs font-bold ${process.step === 'car_arrival' ? 'bg-blue-500 text-white' :
                    process.step === 'conveyor_pickup' ? 'bg-yellow-500 text-gray-900' :
                      process.step === 'color_change' ? 'bg-orange-500 text-white' : 'bg-gray-500 text-white'
                  }`}>
                  {process.step?.replace('_', ' ').toUpperCase()}
                </span>
                <span className="text-gray-400 text-xs">
                  {new Date(process.timestamp).toLocaleTimeString()}
                </span>
              </div>

              <div className="space-y-2">
                {process.details?.color && (
                  <div className="flex items-center space-x-2">
                    <div
                      className="w-4 h-4 rounded border"
                      style={{ backgroundColor: colorMap[process.details.color]?.color }}
                    ></div>
                    <span className="text-white font-semibold text-sm">{process.details.color}</span>
                  </div>
                )}
              </div>
            </div>
          ))}

          {processHistory.length === 0 && (
            <div className="flex-shrink-0 bg-gray-900 rounded-xl p-8 border-2 border-dashed border-gray-700 min-w-64 flex flex-col items-center justify-center text-center">
              <div className="text-gray-500 text-sm">
                No process history yet.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  // Buffer Line Component
  const BufferLine = ({ line }) => {
    if (!line) return <div>Error: Line data missing</div>;

    return (
      <div className="mb-3 flex items-center">
        <div className="flex items-center mr-3 w-12">
          <span className="text-white font-semibold text-sm">{line.id}</span>
        </div>

        <div className="flex items-center space-x-1 bg-gray-800 rounded-xl px-3 py-2 flex-1 min-h-12 border border-gray-700">
          <div className="text-gray-400 text-xs mr-2">
            {line.current}/{line.capacity}
          </div>

          <div className="flex-1 flex items-center space-x-1 overflow-x-auto">
            {line.vehicles.map((vehicleColor, index) => (
              <div key={index} className="flex-shrink-0">
                <VehicleIcon color={colorMap[vehicleColor]?.color || '#9CA3AF'} size="small" />
              </div>
            ))}
            {line.vehicles.length === 0 && (
              <div className="text-gray-500 text-xs italic">Empty</div>
            )}
          </div>
        </div>
      </div>
    );
  };

  // Oven Display Component
  const OvenDisplay = ({ ovenNumber, lines = [] }) => (
    <div className="bg-gray-900 rounded-lg p-4 border border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-white font-bold text-lg">Oven {ovenNumber}</h3>
          <p className="text-gray-400 text-sm">
            Lanes {ovenNumber === 1 ? '1-4' : '5-9'}
          </p>
        </div>
      </div>

      <div className="space-y-2">
        {lines.map((line, index) => (
          <BufferLine key={line?.id || index} line={line} />
        ))}
      </div>
    </div>
  );

  // Default data
  const defaultData = {
    buffer_lanes: {
      oven1: Array(4).fill().map((_, i) => ({
        id: `L${i + 1}`, capacity: 14, current: 0, vehicles: []
      })),
      oven2: Array(5).fill().map((_, i) => ({
        id: `L${i + 5}`, capacity: 16, current: 0, vehicles: []
      }))
    },
    conveyer: {
      current_color: null,
      total_picks: 0,
      color_changes: 0,
      recent_sequence: []
    },
    kpis: {
      throughput: 0,
      targetJPH: 900,
      colorChangeovers: 0,
      bufferUtilization: 0,
      ovenEfficiency: 94.2,
      totalVehicles: 0,
      overflowPenalties: 0
    }
  };

  const displayData = systemState || defaultData;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-white text-2xl font-bold">Conveyor Sequencing System</h1>
          <p className="text-gray-400 text-sm">Real-time Simulation</p>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className={`rounded-full w-3 h-3 ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
            <span className="text-white text-sm">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
      </div>

      {/* Control Panel */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 mb-6">
        <div className="flex items-center space-x-3">
          <button
            onClick={startSimulation}
            disabled={simulationStatus === 'running' || !isConnected}
            className={`px-6 py-3 rounded-lg font-bold ${simulationStatus === 'running' || !isConnected
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-700 text-white'
              }`}
          >
            Start Simulation
          </button>

          <button
            onClick={stopSimulation}
            disabled={simulationStatus !== 'running' || !isConnected}
            className={`px-6 py-3 rounded-lg font-bold ${simulationStatus !== 'running' || !isConnected
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-red-600 hover:bg-red-700 text-white'
              }`}
          >
            Stop Simulation
          </button>

          <button
            onClick={resetSystem}
            disabled={!isConnected}
            className={`px-6 py-3 rounded-lg font-bold ${!isConnected
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
              }`}
          >
            Reset System
          </button>
        </div>

        {!isConnected && (
          <div className="mt-3 p-3 bg-red-900 bg-opacity-50 rounded-lg border border-red-700">
            <div className="text-red-200">
              Backend not connected. Make sure the Python server is running on port 8000.
            </div>
          </div>
        )}
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-6 gap-4 mb-6">
        <div className="bg-blue-600 rounded-lg p-4">
          <p className="text-blue-200 text-xs mb-1">Throughput</p>
          <p className="text-white text-2xl font-bold">{displayData.kpis.throughput}</p>
        </div>
        <div className="bg-green-600 rounded-lg p-4">
          <p className="text-green-200 text-xs mb-1">Efficiency</p>
          <p className="text-white text-2xl font-bold">{displayData.kpis.ovenEfficiency}%</p>
        </div>
        <div className="bg-yellow-600 rounded-lg p-4">
          <p className="text-yellow-200 text-xs mb-1">Changeovers</p>
          <p className="text-white text-2xl font-bold">{displayData.kpis.colorChangeovers}</p>
        </div>
        <div className="bg-purple-600 rounded-lg p-4">
          <p className="text-purple-200 text-xs mb-1">Buffer Usage</p>
          <p className="text-white text-2xl font-bold">{displayData.kpis.bufferUtilization}%</p>
        </div>
        <div className="bg-red-600 rounded-lg p-4">
          <p className="text-red-200 text-xs mb-1">Overflow</p>
          <p className="text-white text-2xl font-bold">{displayData.kpis.overflowPenalties}</p>
        </div>
        <div className="bg-cyan-600 rounded-lg p-4">
          <p className="text-cyan-200 text-xs mb-1">Total Vehicles</p>
          <p className="text-white text-2xl font-bold">{displayData.kpis.totalVehicles}</p>
        </div>
      </div>
      <ConveyorBeltSequence
            sequence={displayData.conveyer?.recent_sequence || []}
            currentColor={displayData.conveyer?.current_color}
            stats={displayData.conveyer || {}}
          />
    
        {/* Ovens Section */}
        <div className="flex flex-col w-[100%] gap-6 mt-10">
          <OvenDisplay ovenNumber={1} lines={displayData.buffer_lanes.oven1} />
          <OvenDisplay ovenNumber={2} lines={displayData.buffer_lanes.oven2} />
        </div>

        {/* Main Content */}
        {/* <div className=" flex flex-col w-[40%] gap-6 mb-6 ml-10  h-[70%] relative top-40">
          

          {/* <RealTimeProcessFlow processHistory={processHistory} /> */}
        {/* </div>  */}
    </div>
  );
};

export default ConveyorSequencingDashboard;