import { ShopScreen } from "@/components/shop/shop-screen"

export default async function UserShopPage({ params }: { params: Promise<{ userId: string }> }) {
  const { userId } = await params
  return <ShopScreen userId={userId} />
}
