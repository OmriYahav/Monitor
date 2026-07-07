import './globals.css';
import Link from 'next/link';
export default function RootLayout({children}:{children:React.ReactNode}){return <html><body><nav className="nav"><b>network-monitor</b><Link href="/">Dashboard</Link><Link href="/devices">Devices</Link><Link href="/alerts">Alerts</Link></nav><main className="container">{children}</main></body></html>}
