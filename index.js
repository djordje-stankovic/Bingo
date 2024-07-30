const puppeteer = require('puppeteer');
const fs = require('fs');
const cron = require('node-cron');
const simpleGit = require('simple-git');
const { Console } = require('console');



function myTask() {
    (async () => {
        function delay(ms) {
            return new Promise((resolve) => {
              setTimeout(resolve, ms);
            });
          }
        let numbers = [];
        let vremeIgriceCekano = false;
        let mainGameCekano = false;
        //ovde ide {headless: 'new'} ako hoces da se ne pali brow
        await delay(30000); // Sačekaj 20 sekundi
        const browser = await puppeteer.launch({
            headless: 'new',
            args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
            env: { TZ: 'Europe/Belgrade' }  // Postavite vremensku zonu na Beograd
          });
        
        const page = await browser.newPage();
        await page.setUserAgent("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36");
        // await page.reload({waitUntil: 'networkidle2'});
        try { //{ timeout: 130000, waitUntil: 'domcontentloaded' }
            await page.goto('https://lucky-betting.mozzartbet.com/lucky6-web/', { timeout: 50000 }); //await page.goto('https://lucky-betting.mozzartbet.com/lucky6-web/');
            await page.waitForTimeout(3000);
            // await page.reload();
            await page.waitForTimeout(3000);
            const game = '.game';
            const mainGameSelector = '.main-game';
            console.log('Sacekao Vreme');
            if (!vremeIgriceCekano) {
                const goldElements = await page.$$eval('.gold', (elements) => {
                    return elements.map((el) => el.textContent.trim());
                });
                const currentDate = new Date(new Date().toLocaleString('en-US', { timeZone: 'Europe/Belgrade' }));

                const options = {
                    day: 'numeric',
                    month: 'numeric',
                    year: 'numeric',
                    hour12: false,
                    timeZone: 'Europe/Belgrade'
                };
                const formattedDateTime = currentDate.toLocaleDateString('sr-RS', options);
                console.log(goldElements);
                if (goldElements.length >= 3) {

                    const dataToWrite = `${formattedDateTime} - ${goldElements[2]} :`;
                    console.log(dataToWrite);
                    numbers.push(dataToWrite);
                    vremeIgriceCekano = true;
                }
            }
            
            console.log('Cekam main game');
            if (!mainGameCekano) {
                console.log('uso i cekam main game')
                await page.waitForSelector(mainGameSelector, { timeout: 30000 });
                console.log('true main game')

                mainGameCekano = true;
            }
            const mainGameDiv = await page.$('.main-game');
            console.log('Sacekao main game');
            if (mainGameDiv) {
                const drumBoxWrapDiv = await mainGameDiv.$('.drumBoxWrap');
                if (drumBoxWrapDiv) {
                    const firstFiveDivs = await drumBoxWrapDiv.$$('.first-five');
                    for (const firstFiveDiv of firstFiveDivs) {
                        const imgElement = await firstFiveDiv.$('img');
                        const imgSrc = await imgElement.evaluate((el) => el.getAttribute('src'));
                        const parts = imgSrc.split('/');
                        const lastPart = parts[parts.length - 1];
                        const number = lastPart.split('.')[0];
                        console.log(number);
                        numbers.push(number);
                    }


                    const lastBallInsideSelector = '.ball-inside:last-child img';
                    await page.waitForSelector(lastBallInsideSelector, { visible: true });


                    await page.waitForFunction(() => {
                        console.log('Sacekao sve lopte');
                        const ballsTable = document.querySelector('.ballsTable');
                        const subColumnElements = ballsTable?.querySelectorAll('.sub-column');
                        if (ballsTable && subColumnElements) {
                            return Array.from(subColumnElements).every((element) => {
                                const h6Element = element.querySelector('h6');
                                const imgElementOfBall = element.querySelector('img');
                                return h6Element && imgElementOfBall;
                            });
                        }
                        return false;
                    }, { timeout: 130000 });


                    const ballsTable = await page.$('.ballsTable');
                    const subColumnElements = await ballsTable.$$('.sub-column');
                    for (const subColumnElement of subColumnElements) {
                        const h6Element = await subColumnElement.$('h6');
                        const imgElementOfBall = await subColumnElement.$('img');
                        if (h6Element && imgElementOfBall) {
                            const h6Text = await h6Element.evaluate((el) => el.textContent.trim());
                            const imgSrc = await imgElementOfBall.evaluate((el) => el.getAttribute('src'));
                            const parts = imgSrc.split('/');
                            const lastPart = parts[parts.length - 1];
                            const imgNumber = lastPart.split('.')[0];
                            numbers.push(imgNumber);
                        }
                    }
                } else {
                    console.log('Nije pronađen div sa klasom "drumBoxWrap".');
                }
            } else {
                console.log('Nije pronađen div sa klasom "main-game".');
            }
           

            fs.readFile('outputNovi2.txt', 'utf8', (err, data) => {
                if (err) throw err;
                const sviBrojevi = data.split('\n');
                console.log(numbers);
                sviBrojevi.push(numbers.join(','));
                fs.writeFile('outputNovi2.txt', sviBrojevi.join('\n'), (err) => {
                    if (err) throw err;
                    console.log('Dodan red sa novom listom u datoteku.');
                });
                // const git = simpleGit();
                // (async () => {
                //     try {
                //       await git.add('outputNovi2.txt');
                //       await git.commit('Dodat novi red u output.txt');
                //       await git.push();
                //       console.log('Dodao na git');
                //     } catch (error) {
                //       console.error('Greška pri slanju na git:', error);
                //     }
                //   })()
                
            });

            await browser.close();
        } catch (error) {

        } finally {
            await browser.close();
        }
    })
        ();

}

myTask();


cron.schedule('*/5 * * * *', myTask);
