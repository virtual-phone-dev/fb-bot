
const instructionsDisponibles = [
	{
		id: "New Context",
		code: `
context = await browser.new_context()
`
	},

	{
		id: "Cookies",
		code: `
cookies = charger_cookies(fichier_cookie)
await context.add_cookies(cookies)
`
	},

	{
		id: "Nav (Context + Cookies)",
		code: `
context = await browser.new_context()
cookies = charger_cookies(fichier_cookie)
await context.add_cookies(cookies)
`
	},

	{
		code: `
page = await context.new_page()
await appliquer_stealth(page)
`
	}
];
