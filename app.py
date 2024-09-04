from crawler.crawler import Crawler

if __name__ == "__main__":
    url_list = [
        # "https://www.vietjack.com/toan-11-kn/trac-nghiem-bai-1-gia-tri-luong-giac-cua-goc-luong-giac.jsp",
        # "https://www.vietjack.com/toan-11-kn/trac-nghiem-bai-2-cong-thuc-luong-giac.jsp",
        # "https://www.vietjack.com/toan-11-kn/trac-nghiem-bai-3-ham-so-luong-giac.jsp",
        # "https://www.vietjack.com/toan-11-kn/trac-nghiem-bai-4-phuong-trinh-luong-giac-co-ban.jsp",
        # "https://www.vietjack.com/toan-11-kn/trac-nghiem-bai-tap-cuoi-chuong-1.jsp",
        "https://www.vietjack.com/toan-11-cd/trac-nghiem-bai-1-goc-luong-giac-gia-tri-luong-giac-cua-goc-luong-giac.jsp",
        "https://www.vietjack.com/toan-11-cd/trac-nghiem-bai-2-cac-phep-bien-doi-luong-giac.jsp",
        "https://www.vietjack.com/toan-11-cd/trac-nghiem-bai-3-ham-so-luong-giac-va-do-thi.jsp",
        "https://www.vietjack.com/toan-11-cd/trac-nghiem-bai-4-phuong-trinh-luong-giac-co-ban.jsp",
        "https://www.vietjack.com/toan-11-cd/trac-nghiem-bai-tap-cuoi-chuong-1.jsp",
    ]
    model_name = "llama3-70b-8192"
    crawler = Crawler(url_list, model_name)
    print("INSTRUCTION: " + crawler.system_prompt)
    crawler.crawl()
    crawler.save("math_cd_reasoning.csv")
