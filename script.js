fetch('data/output.json')
  .then(response => response.json())
  .then(data => {

    document.getElementById('updateTime').innerText =
      'Last Updated: ' + data.lastUpdated;

    let top20HTML = '';

    data.top20.forEach(stock => {

      top20HTML += `
        <tr>
          <td>${stock.symbol}</td>
          <td>${stock.return3M}%</td>
          <td>${stock.return6M}%</td>
          <td>${stock.return12M}%</td>
          <td>${stock.momentumScore}</td>
        </tr>
      `;

    });

    document.getElementById('top20Table').innerHTML = top20HTML;

    let portfolioHTML = '';

    data.portfolio.forEach(stock => {

      portfolioHTML += `
        <tr>
          <td>${stock.symbol}</td>
          <td>₹${stock.price}</td>
          <td>${stock.quantity}</td>
          <td>₹${stock.investedAmount}</td>
          <td>${stock.momentumScore}</td>
        </tr>
      `;

    });

    document.getElementById('portfolioTable').innerHTML = portfolioHTML;

  })
  .catch(error => console.log(error));
