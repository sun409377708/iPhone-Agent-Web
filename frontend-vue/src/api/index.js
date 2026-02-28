// 动态获取后端地址：如果是通过局域网 IP 访问，则使用相同的 IP 访问后端
const getApiBaseUrl = () => {
  const hostname = window.location.hostname
  // 如果是 localhost 或 127.0.0.1，使用 localhost
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:5001'
  }
  // 否则使用当前访问的 IP 地址
  return `http://${hostname}:5001`
}

const API_BASE_URL = getApiBaseUrl()

export async function fetchDevices() {
  const response = await fetch(`${API_BASE_URL}/api/devices`)
  if (!response.ok) {
    throw new Error('Failed to fetch devices')
  }
  return response.json()
}

export async function runTask(instruction, deviceId) {
  const response = await fetch(`${API_BASE_URL}/run`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ task: instruction, device_id: deviceId }),
  })
  if (!response.ok) {
    throw new Error('Failed to run task')
  }
  return response.json()
}

export async function fetchHistory() {
  const response = await fetch(`${API_BASE_URL}/api/history`)
  if (!response.ok) {
    throw new Error('Failed to fetch history')
  }
  return response.json()
}

export function createLogStream(onMessage, onError) {
  const eventSource = new EventSource(`${API_BASE_URL}/logs`)
  
  eventSource.onmessage = (event) => {
    try {
      // 后端发送的是纯文本，不是 JSON
      const message = event.data
      onMessage(message)
    } catch (error) {
      console.error('Failed to parse log message:', error, event.data)
    }
  }
  
  eventSource.onerror = (error) => {
    console.error('EventSource error:', error)
    onError(error)
    eventSource.close()
  }
  
  return eventSource
}

export async function getScreenshot(deviceId) {
  const url = deviceId 
    ? `${API_BASE_URL}/api/screenshot?device_id=${deviceId}`
    : `${API_BASE_URL}/api/screenshot`
  const response = await fetch(url)
  if (!response.ok) {
    throw new Error('Failed to get screenshot')
  }
  return response.json()
}

export function getMjpegStreamUrl(deviceId) {
  if (!deviceId) return null
  return `${API_BASE_URL}/api/devices/${deviceId}/mjpeg`
}

export async function controlTap(deviceId, xRatio, yRatio) {
  const response = await fetch(`${API_BASE_URL}/api/devices/${deviceId}/control/tap`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ x_ratio: xRatio, y_ratio: yRatio }),
  })
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || 'Failed to tap')
  }
  return response.json()
}

export async function controlSwipe(deviceId, startXRatio, startYRatio, endXRatio, endYRatio, durationMs = 350) {
  const response = await fetch(`${API_BASE_URL}/api/devices/${deviceId}/control/swipe`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      start_x_ratio: startXRatio,
      start_y_ratio: startYRatio,
      end_x_ratio: endXRatio,
      end_y_ratio: endYRatio,
      duration_ms: durationMs,
    }),
  })
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || 'Failed to swipe')
  }
  return response.json()
}

export async function wakeScreen(deviceId) {
  const response = await fetch(`${API_BASE_URL}/api/devices/${deviceId}/control/wake`, {
    method: 'POST',
  })
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || 'Failed to wake screen')
  }
  return response.json()
}

export async function goHome(deviceId) {
  const response = await fetch(`${API_BASE_URL}/api/devices/${deviceId}/control/home`, {
    method: 'POST',
  })
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || 'Failed to go home')
  }
  return response.json()
}

// ==================== 测试用例管理 ====================

export async function getTestCases(category = null) {
  const url = category 
    ? `${API_BASE_URL}/api/test-cases?category=${category}`
    : `${API_BASE_URL}/api/test-cases`
  const response = await fetch(url)
  if (!response.ok) {
    throw new Error('Failed to fetch test cases')
  }
  return response.json()
}

export async function createTestCase(data) {
  const response = await fetch(`${API_BASE_URL}/api/test-cases`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    throw new Error('Failed to create test case')
  }
  return response.json()
}

export async function updateTestCase(id, data) {
  const response = await fetch(`${API_BASE_URL}/api/test-cases/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    throw new Error('Failed to update test case')
  }
  return response.json()
}

export async function deleteTestCase(id) {
  const response = await fetch(`${API_BASE_URL}/api/test-cases/${id}`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    throw new Error('Failed to delete test case')
  }
  return response.json()
}

export async function initTestCases() {
  const response = await fetch(`${API_BASE_URL}/api/test-cases/init`, {
    method: 'POST',
  })
  if (!response.ok) {
    throw new Error('Failed to initialize test cases')
  }
  return response.json()
}

// ==================== WDA 控制 ====================

export async function startWDA(deviceId) {
  const response = await fetch(`${API_BASE_URL}/api/devices/${deviceId}/wda/start`, {
    method: 'POST',
  })
  if (!response.ok) {
    throw new Error('Failed to start WDA')
  }
  return response.json()
}

export async function stopWDA(deviceId) {
  const response = await fetch(`${API_BASE_URL}/api/devices/${deviceId}/wda/stop`, {
    method: 'POST',
  })
  if (!response.ok) {
    throw new Error('Failed to stop WDA')
  }
  return response.json()
}

export async function getWDAStatus(deviceId) {
  const response = await fetch(`${API_BASE_URL}/api/devices/${deviceId}/wda/status`)
  if (!response.ok) {
    throw new Error('Failed to get WDA status')
  }
  return response.json()
}
