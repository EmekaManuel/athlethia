"""
Example usage of Athlethia API
"""
import httpx
import asyncio


async def scan_url_example():
    """Example of scanning a URL"""
    async with httpx.AsyncClient() as client:
        # Scan a URL
        response = await client.post(
            "http://localhost:8000/api/v1/scan",
            json={"url": "https://example.com"}
        )
        
        result = response.json()
        print(f"URL: {result['url']}")
        print(f"Is Scam: {result['is_scam']}")
        print(f"Scam Score: {result['scam_score']:.2%}")
        print(f"Reasons: {', '.join(result['reasons'])}")


async def get_stats_example():
    """Example of getting statistics"""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/api/v1/stats")
        stats = response.json()
        print(f"Total Scans: {stats['total_scans']}")
        print(f"Scam Detections: {stats['scam_detections']}")
        print(f"Detection Rate: {stats['detection_rate']:.2f}%")


async def report_scam_example():
    """Example of reporting a scam"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/report",
            params={
                "url": "https://suspicious-site.com",
                "platform": "telegram",
                "reason": "Phishing attempt"
            }
        )
        print(response.json())


if __name__ == "__main__":
    print("=== Athlethia API Examples ===\n")
    
    print("1. Scanning a URL:")
    asyncio.run(scan_url_example())
    
    print("\n2. Getting Statistics:")
    asyncio.run(get_stats_example())
    
    print("\n3. Reporting a Scam:")
    asyncio.run(report_scam_example())

