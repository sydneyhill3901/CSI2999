const writePriceData = (shop,resultAry) => {
		/* Inputs: 
			shop = "shopName"
			resultsAry = [{"name": prodname, "url": "link" , "price" : "price", "shipping_cost" : "shipping cost" }...]
			Adds a bulleted list of the phones with a link to purchase, the cost, and shipping cost if available
		*/ 
		try {
			let priceDiv = $(`#${shop}_prices`);
			let oldPara = priceDiv.children(".wait_message")
			// Write store data to a price list, or inform that no results found
			if (resultAry != null) {
				let innerHTML = "<ul class=\"priceList\">\n";
				// Add results as list elements w/ links, and data presented in a para element
				//for (let result of resultAry){ 
				resultAry.forEach( (result) => {
					let name = result.name, price = result.price, link = result.url;	
					let item = "\t\t<li>" + `\n\t\t\t<a href="${link}">${name}</a>\n\t\t\t`;
					item += `<p>Price: \$${price}</p>\n\t\t</li>`
					//console.log("\n" + item);
					innerHTML += item;
				});
				//}
				innerHTML += "\n</ul>";
				priceDiv.append($(innerHTML));
			} 
			else {
				priceDiv.append(`<p class=\"noPrices\">Sorry, no ${shop} prices found</p>`)
			}
			oldPara.remove();
		} catch (error) {
			console.log(error);
		}	
}

