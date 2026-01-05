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

export async function runTask(instruction) {
  const response = await fetch(`${API_BASE_URL}/run`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ task: instruction }),
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

export async function getScreenshot() {
  const response = await fetch(`${API_BASE_URL}/api/screenshot`)
  if (!response.ok) {
    throw new Error('Failed to get screenshot')
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
