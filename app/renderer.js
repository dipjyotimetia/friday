// renderer.js
const generateForm = document.getElementById('generate-form')
const crawlerForm = document.getElementById('crawler-form')
const outputText = document.getElementById('output-text')
const tabButtons = document.querySelectorAll('.tab-btn')
const tabContents = document.querySelectorAll('.tab-content')

// Tab switching
tabButtons.forEach(button => {
  button.addEventListener('click', () => {
    const tabId = button.getAttribute('data-tab')
    
    // Update active states
    tabButtons.forEach(btn => btn.classList.remove('active'))
    tabContents.forEach(content => content.classList.remove('active'))
    
    button.classList.add('active')
    document.getElementById(tabId).classList.add('active')
    
    // Clear output when switching tabs
    outputText.textContent = ''
  })
})

// API endpoint
const API_URL = 'http://localhost:8080'

generateForm.addEventListener('submit', async (e) => {
  e.preventDefault()
  
  const data = {
    jira_key: document.getElementById('jira-key').value,
    gh_issue: document.getElementById('gh-issue').value,
    gh_repo: document.getElementById('gh-repo').value,
    confluence_id: document.getElementById('confluence-id').value,
    output: document.getElementById('output').value
  }

  try {
    const response = await fetch(`${API_URL}/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
    
    const result = await response.json()
    outputText.textContent = JSON.stringify(result, null, 2)
  } catch (err) {
    outputText.textContent = `Error: ${err.message}`
  }
})

crawlerForm.addEventListener('submit', async (e) => {
  e.preventDefault()
  
  const data = {
    url: document.getElementById('url').value,
    provider: document.getElementById('provider').value,
    persist_dir: './data/chroma',
    max_pages: parseInt(document.getElementById('max-pages').value),
    same_domain: document.getElementById('same-domain').checked
  }

  try {
    const response = await fetch(`${API_URL}/crawl`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
    
    const result = await response.json()
    outputText.textContent = JSON.stringify(result, null, 2) 
  } catch (err) {
    outputText.textContent = `Error: ${err.message}`
  }
})