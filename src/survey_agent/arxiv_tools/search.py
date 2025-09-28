import arxiv
from typing import List, Dict, Any, Optional
from fuzzywuzzy import fuzz
import time
import signal

def search_papers_by_terms(terms: List[str], max_results: int = 100, logic: str = "AND", date: Optional[str] = None, date_range: Optional[List[str]] = None, multi_terms: Optional[List[List[str]]] = None) -> List[Any]:
    """
    Search for papers on arXiv based on a list of terms.
    
    Args:
        terms: List of search terms (single group)
        max_results: Maximum number of results to return
        logic: Logic operator for combining terms ("AND" or "OR")
        date: Specific date to search (format: YYYY-MM-DD)
        date_range: Date range to search (format: [start_date, end_date] as YYYY-MM-DD)
        multi_terms: List of term groups, generates all combinations (Cartesian product)
        
    Returns:
        List of paper dictionaries
    """
    client = arxiv.Client()
    
    # Use multi_terms if provided, otherwise use single terms list
    if multi_terms and len(multi_terms) > 0:
        # Multi-group search: generate all combinations (Cartesian product)
        import itertools
        
        # Generate all combinations
        all_combinations = list(itertools.product(*multi_terms))
        
        print(f"🔍 生成 {len(all_combinations)} 种组合:")
        for i, combo in enumerate(all_combinations, 1):
            print(f"  {i}. {' + '.join(combo)}")
        
        all_results = []
        
        # Search for each combination
        for combo in all_combinations:
            # Create query for this combination (both title and abstract)
            combo_title_query = " AND ".join([f'ti:"{term}"' for term in combo])
            combo_abs_query = " AND ".join([f'abs:"{term}"' for term in combo])
            combo_query = f"({combo_title_query}) OR ({combo_abs_query})"
            
            # Add date filter if specified
            query_string = combo_query
            if date:
                date_str = date.replace('-', '')
                from datetime import datetime, timedelta
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                next_day = date_obj + timedelta(days=1)
                next_day_str = next_day.strftime('%Y%m%d')
                query_string += f" AND submittedDate:[{date_str} TO {next_day_str}]"
            elif date_range and len(date_range) == 2:
                start_date = date_range[0].replace('-', '')
                end_date = date_range[1].replace('-', '')
                query_string += f" AND submittedDate:[{start_date} TO {end_date}]"
            
            try:
                search = arxiv.Search(
                    query=query_string,
                    max_results=max_results // len(all_combinations) + 1,  # Distribute max_results across combinations
                    sort_by=arxiv.SortCriterion.SubmittedDate
                )
                
                combo_results = list(client.results(search))
                all_results.extend(combo_results)
                print(f"  ✅ {' + '.join(combo)}: 找到 {len(combo_results)} 篇论文")
                
            except Exception as e:
                print(f"  ❌ {' + '.join(combo)}: 搜索失败 - {e}")
                continue
        
        # Remove duplicates based on paper URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            if result.entry_id not in seen_urls:
                seen_urls.add(result.entry_id)
                unique_results.append(result)
        
        return unique_results
        
    else:
        # Single group search (original logic)
        operator = " AND " if logic.upper() == "AND" else " OR "
        
        # Create query string for title search
        query_string_title = operator.join([f'ti:"{term}"' for term in terms])
        
        # Create query string for abstract search
        query_string_abs = operator.join([f'abs:"{term}"' for term in terms])
        
        # Combine both queries
        query_string = f"({query_string_title}) OR ({query_string_abs})"
        
        # Add date filter if specified
        if date:
            date_str = date.replace('-', '')
            from datetime import datetime, timedelta
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            next_day = date_obj + timedelta(days=1)
            next_day_str = next_day.strftime('%Y%m%d')
            query_string += f" AND submittedDate:[{date_str} TO {next_day_str}]"
        elif date_range and len(date_range) == 2:
            start_date = date_range[0].replace('-', '')
            end_date = date_range[1].replace('-', '')
            query_string += f" AND submittedDate:[{start_date} TO {end_date}]"
        
        search = arxiv.Search(
            query=query_string,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        
        results = list(client.results(search))
        return results

def search_paper_by_title(paper_title: str, timeout: int = 30) -> Optional[Any]:
    """
    Search for a specific paper by title with timeout.
    
    Args:
        paper_title: The title of the paper to search for
        timeout: Timeout in seconds for the search
        
    Returns:
        Paper object if found, None otherwise
    """
    # Clean up title for search
    tidy_title = paper_title.replace(':', '').strip()
    tidy_title = ' '.join(tidy_title.split())  # Remove extra spaces
    
    def timeout_handler(signum, frame):
        raise TimeoutError("Search timeout")
    
    # Set up timeout
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    
    try:
        client = arxiv.Client()
        search = arxiv.Search(query=f'ti:{tidy_title}', max_results=20)
        
        results = list(client.results(search))
        if not results:
            return None
        
        # Find the best match using fuzzy matching
        best_match = max(results, key=lambda result: fuzz.ratio(paper_title.lower(), result.title.lower()))
        return best_match
        
    except TimeoutError:
        print(f"   ⏰ 搜索超时 ({timeout}秒)")
        return None
    except Exception as e:
        print(f"   ❌ 搜索错误: {e}")
        return None
    finally:
        # Cancel timeout and restore old handler
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)

def search_papers(terms=None, titles=None, max_results=100, logic="AND", date=None, date_range=None, multi_terms=None) -> List[Any]:
    """
    Search for papers on arXiv by terms or titles.
    
    Args:
        terms: List of search terms (e.g., ["VLM", "Games"]) - single group
        titles: List of paper titles to search for
        max_results: Maximum number of results per search
        logic: Logic operator for combining terms ("AND" or "OR") - only used for single group
        date: Specific date to search (format: YYYY-MM-DD)
        date_range: Date range to search (format: [start_date, end_date] as YYYY-MM-DD)
        multi_terms: List of term groups, each group uses OR internally, groups use AND between them
        
    Returns:
        List of paper objects
    """
    results = []
    date_info = ""
    if date:
        date_info = f" (日期: {date})"
    elif date_range:
        date_info = f" (日期范围: {date_range[0]} 到 {date_range[1]})"
    
    # 优先使用multi_terms，如果提供了的话
    if multi_terms and len(multi_terms) > 0:
        print(f"🔍 多组搜索中... {multi_terms} (笛卡尔积组合){date_info}")
        results.extend(search_papers_by_terms(terms=[], max_results=max_results, logic=logic, date=date, date_range=date_range, multi_terms=multi_terms))
    elif terms:
        if isinstance(terms[0], list):
            # Multiple term groups (legacy support)
            print(f"🔍 多组搜索中... {terms} (逻辑: {logic}){date_info}")
            for term_group in terms:
                results.extend(search_papers_by_terms(term_group, max_results, logic, date, date_range))
        else:
            # Single term group
            print(f"🔍 搜索中... {terms} (逻辑: {logic}){date_info}")
            results.extend(search_papers_by_terms(terms, max_results, logic, date, date_range))
    
    if titles:
        print(f"🔍 标题搜索中... 共 {len(titles)} 个标题")
        if len(titles) > 10:
            print(f"   前5个标题: {titles[:5]}")
            print(f"   ... 还有 {len(titles) - 5} 个标题")
        else:
            print(f"   标题列表: {titles}")
        
        found_count = 0
        timeout_count = 0
        error_count = 0
        
        for i, title in enumerate(titles, 1):
            print(f"🔍 [{i}/{len(titles)}] 搜索论文: {title[:60]}{'...' if len(title) > 60 else ''}")
            
            start_time = time.time()
            paper = search_paper_by_title(title, timeout=30)
            search_time = time.time() - start_time
            
            if paper:
                results.append(paper)
                found_count += 1
                print(f"   ✅ 找到论文 ({search_time:.1f}s): {paper.title[:60]}{'...' if len(paper.title) > 60 else ''}")
            else:
                print(f"   ❌ 没有找到论文 ({search_time:.1f}s)")
            
            # 每10个标题显示一次进度统计
            if i % 10 == 0 or i == len(titles):
                print(f"   📊 进度统计: 已搜索 {i}/{len(titles)}, 找到 {found_count} 篇")
        
        print(f"\n📈 标题搜索统计:")
        print(f"   总标题数: {len(titles)}")
        print(f"   找到论文: {found_count}")
        print(f"   未找到: {len(titles) - found_count}")
    
    # 打印搜索到的论文信息
    print(f"\n📚 搜索完成！共找到 {len(results)} 篇论文：")
    print("=" * 100)
    for i, paper in enumerate(results, 1):
        title = paper.title
        
        print(f"{i:3d}. {title}")
        print(f"     👥 作者: {', '.join([str(author) for author in paper.authors])}")
        print(f"     📅 发布日期: {paper.published}")
        print(f"     🔗 URL: {paper.entry_id}")
        print("-" * 100)
    
    return results 