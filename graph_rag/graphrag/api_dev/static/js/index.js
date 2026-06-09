/**
 * GraphRAG 标准查询页逻辑
 * API 接口: POST /api/query
 */

function ensureMarkedLoaded() {
    if (typeof marked !== 'undefined') {
        return Promise.resolve();
    }

    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/marked@4.0.2/marked.min.js';
        script.onload = () => resolve();
        script.onerror = () => reject(new Error('无法加载 Markdown 渲染库'));
        document.head.appendChild(script);
    });
}

function showError(message) {
    const errorElement = document.getElementById('error');
    errorElement.textContent = message;
    errorElement.style.display = 'block';

    setTimeout(() => {
        errorElement.style.opacity = '0';
        setTimeout(() => {
            errorElement.style.display = 'none';
            errorElement.style.opacity = '1';
        }, 500);
    }, 5000);
}

function renderResponse(text) {
    const resultContent = document.getElementById('result-content');

    if (typeof marked !== 'undefined') {
        resultContent.innerHTML = marked.parse(text);
        return;
    }

    resultContent.innerHTML = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n\n/g, '<br><br>')
        .replace(/\n###\s(.*?)\n/g, '<br><h3>$1</h3><br>');
}

async function submitQuery() {
    const query = document.getElementById('query').value.trim();
    if (!query) {
        showError('请输入查询内容');
        return;
    }

    const payload = {
        query,
        query_type: document.getElementById('query-type').value,
        response_type: document.getElementById('response-type').value,
        community_level: parseInt(document.getElementById('community-level').value, 10),
        dynamic_community_selection: document.getElementById('dynamic-community-selection').checked,
    };

    document.getElementById('result').style.display = 'none';
    document.getElementById('error').style.display = 'none';
    document.getElementById('loading').style.display = 'block';

    try {
        await ensureMarkedLoaded();

        const response = await fetch('/api/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        document.getElementById('loading').style.display = 'none';

        if (!response.ok) {
            let errorMessage = '查询失败';
            try {
                const errorData = await response.json();
                if (errorData?.detail) {
                    errorMessage = errorData.detail;
                }
            } catch {
                errorMessage = `查询失败 (${response.status}: ${response.statusText})`;
            }
            throw new Error(errorMessage);
        }

        const responseText = await response.text();
        if (!responseText.trim()) {
            throw new Error('服务器返回了空响应');
        }

        const data = JSON.parse(responseText);
        document.getElementById('result').style.display = 'block';

        if (data?.response) {
            renderResponse(data.response);
        } else {
            document.getElementById('result-content').textContent = '服务器返回了空结果';
        }
    } catch (error) {
        document.getElementById('loading').style.display = 'none';
        showError(error.message);
        console.error('请求错误:', error);
    }
}

function bindFormFocusEffects() {
    document.querySelectorAll('input, select, textarea').forEach((element) => {
        element.addEventListener('focus', function () {
            const label = this.parentElement?.querySelector('label');
            if (label) {
                label.style.color = 'var(--primary-color)';
            }
        });

        element.addEventListener('blur', function () {
            const label = this.parentElement?.querySelector('label');
            if (label) {
                label.style.color = '';
            }
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('submit-btn').addEventListener('click', submitQuery);
    bindFormFocusEffects();
});
