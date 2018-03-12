from uuid import UUID

from candytuft.product import Vendor, Store
from candytuft.repository import StoreRepository

CARIOCAWEAR_STORE = Store(id=UUID("fd1e0b6f-9f35-4261-8bf7-4204bc7cff6a"), short_name="carioca", name="CA-RIO­CA Sunga Co", currency="USD", url="https://cariocawear.com")

CARIOCA_VENDOR = Vendor(id=UUID("009b0568-00c6-4c37-b7d4-60de60458ee9"), short_name="carioca", name="CA-RIO­CA Sunga Co", url="https://cariocawear.com")

store_repository = StoreRepository()
store_repository.put(CARIOCAWEAR_STORE)
