import os

get_date_range_description = '''
                        뉴스를 수집하기 위한 시작일과 종료일을 반환합니다.
                        
                        parameters:
                            days: 오늘로부터 며칠 전까지를 조회할지 설정 (기본값: 7)
                        
                        return:
                            (start_date, end_date) 튜플 형태로 시작일과 종료일을 반환합니다.
                        '''


fetch_news_documents_description = '''
                        특정 키워드를 기반으로 뉴스 문서들을 조회합니다.

                        parameters:
                            keyword (str): 키워드
                            ctx (Context): 요청 처리용 컨텍스트 객체
                            start_date (str, 선택): 시작일 (YYYY-MM-DD)
                            end_date (str, 선택): 종료일 (YYYY-MM-DD)

                        return:
                            dict: Dictionary containing news document data matching the complex query criteria
                        '''


fetch_news_comments_by_article_id_list_description = '''
                        여러 뉴스 기사 ID를 기반으로 댓글을 조회합니다. 뉴스기사 ID를 수집하기 위해 반드시 뉴스문서를 먼저 수집해야 합니다. 

                        parameters:
                            article_id_list (list[str]): 뉴스 기사 ID 리스트
                            ctx (Context): 요청 처리용 컨텍스트 객체
                            page_num (int, 선택): 페이지 번호 (기본값: 0)
                            size (int, 선택): 페이지당 댓글 수 (기본값: 50)
                            sort_field (str, 선택): 정렬 기준 필드 (기본값: "like_count")
                            is_asc (bool, 선택): 오름차순 여부 (True: 오름차순, False: 내림차순)

                        return:
                            dict:
                                - contents (list): 댓글 내용 리스트
                                - total_counts (int): 전체 댓글 수
                        '''


fetch_keyword_frequency_description = '''
                        논리 연산자를 포함한 복합 검색 쿼리를 통해 문서 내 단어 빈도를 조회합니다.

                        쿼리 조건:
                        - 메인 키워드는 반드시 포함
                        - 포함 키워드: && (AND), || (OR)
                        - 제외 키워드: ~ (NOT)

                        예:
                            keyword = "iphone"
                            include_keywords = "apple&&release"
                            exclude_keywords = "discount||event||coupon"

                            쿼리: iphone&&(apple&&release)&&~(discount||event||coupon)

                        parameters:
                            keyword: 메인 키워드 (필수 포함)
                            include_keywords: 함께 포함될 키워드들 (AND/OR 사용)
                            exclude_keywords: 제외할 키워드들 (OR 사용)
                            ctx: API 요청용 컨텍스트
                            start_date: 시작일 (YYYY-MM-DD)
                            end_date: 종료일 (YYYY-MM-DD)

                        return:
                            dict: Word frequency analysis results
                        '''
