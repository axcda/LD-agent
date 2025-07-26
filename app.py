#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multimodal Content Analysis Framework
主程序入口 - 优化后的目录结构版本
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import main

if __name__ == "__main__":
    main()