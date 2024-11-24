export async function load() {
  const response = await fetch('http://localhost:8000/api/fetch_robinhood_orders', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ username: 'your_username', password: 'your_password' }) // Replace with actual credentials
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to fetch order history');
  }

  const data = await response.json();
  return {
    orders: data.orders,
  };
}