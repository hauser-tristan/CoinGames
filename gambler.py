
# Libraries
# ---------
from functools import partial
from scipy.stats import binom 

import pandas as pd
import numpy as np


class gambler :
    ''' 
    Create individual players of a coin toss game. 
    Players can choose different stratigies based on 
    how they believe the game is designed. 
    '''

    def __init__(self,game,prior='Jefferies',return_rate=1,bet=1) :
        
        # ... set game ...
        self.game = game
        
        # ... set payout options ...
        self.odds = (1,return_rate)
        self.bet = bet

        # ... keep track of balance ...
        self.balance = pd.Series(index=[0])
        self.balance[0] = 0
        
        # ... set prior ...
        self.posterior = pd.DataFrame(
            columns=['a','b'])        
        if prior == 'Jefferies' : 
            self.posterior.loc[0,'a'] = 0.5
            self.posterior.loc[0,'b'] = 0.5
        elif prior == 'Bayes' : 
            self.posterior.loc[0,'a'] = 1.0
            self.posterior.loc[0,'b'] = 1.0
        elif prior == 'Haldane' :
            self.posterior.loc[0,'a'] = 0.0
            self.posterior.loc[0,'b'] = 0.0
        else :
            print(' +++ No prior specified +++')

    def estm_mu(self,a,b) :
        '''
        Estimate the mean of a beta distribution
        from it's parameters.
        '''
        mu = a/(a+b)
        return mu
    
    def estm_sigma(self,a,b) :
        '''
        Estimate the standard deviation of a beta distribution
        from it's parameters.
        '''
        sigma = np.sqrt((a*b)/(((a+b)**2)+(a+b+1)))
        return sigma

            
    def play_the_game(self,n_games,strategy=None) : 
        
        # ... start from where left off ...
        pick_up_point = self.balance.index[-1]
        for n in range(pick_up_point+1,pick_up_point+n_games+1) :  
            
            # ... play a round ...
            h = self.game()
            
            # ... pay or collect ...
            if h == 0 : 
                self.balance[n] = self.balance[n-1]+(self.odds[1]*self.bet)
            else : 
                self.balance[n] = self.balance[n-1]-(self.odds[0]*self.bet)
                
            # ... update beliefs ...
            self.posterior.loc[n,'a'] = h + self.posterior.loc[n-1,'a']
            self.posterior.loc[n,'b'] = 1 - h + self.posterior.loc[n-1,'b']
            self.mu = self.estm_mu(
                self.posterior.loc[n,'a'],self.posterior.loc[n,'b'])
            self.sigma = self.estm_sigma(
                self.posterior.loc[n,'a'],self.posterior.loc[n,'b'])
            
            if strategy : 
                if strategy == 'learn' :
                    # ... update odds ...
                    prob_tails = 1-self.mu
                    self.odds = (1,(1/prob_tails)-1)                
                if strategy == 'cautious' :
                    # ... update odds ...
                    prob_tails = 1-self.mu
                    self.odds = (1,(1/prob_tails)-1) 
                    # ... update bet ...
                    self.bet = 1-self.sigma
            
    
