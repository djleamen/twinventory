import { ShopScreen } from "@/components/shop/shop-screen"

export default async function UserShopPage({ params }: { params: Promise<{ username: string }> }) {
  const { username } = await params
  return <ShopScreen username={decodeURIComponent(username)} />
}
