import nltk
import ssl

# 尝试创建未验证的 SSL 上下文（如果需要）
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# 下载所需的 nltk 包
nltk.download('punkt', quiet=False)
nltk.download('averaged_perceptron_tagger', quiet=False)
nltk.download('punkt_tab', quiet=False)
nltk.download('averaged_perceptron_tagger_eng')